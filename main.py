from tkinter import *
from tkinter import messagebox
import json
from tkinter import ttk
from datetime import datetime
import os
from PIL import Image, ImageTk
from tkinter import simpledialog

# Класс клиента банка
class Client:
    def __init__(self, client_id, name, balance):
        self.id = client_id
        self.name = name 
        self.balance = balance
    
    def withdraw(self, amount):
        # Снять деньги со счета
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False
    
    def deposit(self, amount):
        # Пополнить счет
        self.balance += amount
        return True
    
    def transfer(self, recipient, amount):
        # Перевести деньги другому клиенту
        if self.balance >= amount:
            self.balance -= amount
            recipient.balance += amount
            return True
        return False
    
    def get_info(self):
        # Получить информацию о клиенте
        return f"Клиент: {self.name}, Баланс: {self.balance}₽"
    
    def to_dict(self):
        # Преобразовать в словарь для сохранения в JSON
        return {
            'id': self.id,
            'name': self.name, 
            'balance': self.balance
        }
        

# Основная банковская система
class BankSystem:
    def __init__(self):
        self.clients = []
        self.load_data()
    
    def load_data(self):
        # Загружаем данные клиентов из JSON файла
        try:
            with open("data.json", "r", encoding='utf-8') as f:
                json_data = json.load(f)
            self.clients = [Client(item['id'], item['name'], item['balance']) for item in json_data]
            print(f"Загружено {len(self.clients)} клиентов")
        except FileNotFoundError:
            self.clients = []
            print("Файл data.json не найден")
    
    def find_client_by_name(self, name):
        # Ищем клиента по имени
        for client in self.clients:
            if client.name == name:
                return client
        return None
    
    def find_clients_for_transfer(self, sender_name, recipient_name):
        # Находим отправителя и получателя для перевода
        sender = None
        recipient = None

        for client in self.clients:
            if client.name == sender_name:
                sender = client
            if client.name == recipient_name:
                recipient = client

        if not sender:
            messagebox.showerror('Ошибка', f'Клиент {sender_name} не найден!')
            return None, None
        if not recipient:
            messagebox.showerror('Ошибка', f'Клиент {recipient_name} не найден!')
            return None, None
        if sender.id == recipient.id:
            messagebox.showerror('Ошибка', 'Нельзя перевести самому себе!')
            return None, None
            
        return sender, recipient
    
    def save_data(self):
        # Сохраняем данные всех клиентов в JSON
        json_data = [client.to_dict() for client in self.clients]
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        print("Данные сохранены")
    
    def get_clients_names(self):
        # Получаем список имен клиентов для выпадающего списка
        return [client.name for client in self.clients]
    
    def transfer_money(self, sender_name, recipient_name, amount):
        # Выполняем перевод между клиентами
        sender, recipient = self.find_clients_for_transfer(sender_name, recipient_name)
        if sender and recipient:
            if sender.transfer(recipient, amount):
                self.save_data()
                return True
        return False
        
    def show_operation_info(self, client, summa, operation_type, recipient=None):
        # Показываем информацию об операции
        if operation_type == 'Перевод' and recipient:
            messagebox.showinfo(title='Успех!', message=
                f'Успешный перевод!\n'
                f'----------------------------------------\n'                        
                f"{client.name} → {recipient.name}: {summa}₽\n"
                f'----------------------------------------\n'
                f"У {client.name}: {client.balance}₽\n"
                f'----------------------------------------\n'
                f"У {recipient.name}: {recipient.balance}₽\n")
        elif operation_type == 'Вывод':
            messagebox.showinfo(title='Успех!', message=
                f'Успешный вывод!\n'
                f'----------------------------------------\n'                        
                f"{client.name} вывел {summa}₽\n"
                f'----------------------------------------\n'
                f"Баланс: {client.balance}₽\n"
                f'----------------------------------------\n')
        elif operation_type == 'Пополнение':
            messagebox.showinfo(title='Успех!', message=
                f'Успешное пополнение!\n'
                f'----------------------------------------\n'                        
                f"{client.name} пополнил на {summa}₽\n"
                f'----------------------------------------\n'
                f"Баланс: {client.balance}₽\n"
                f'----------------------------------------\n')


# Создаем экземпляр банковской системы
bank_system = BankSystem()

# Тестируем систему
print("=== ТЕСТ BankSystem ===")
print(f"Клиенты: {[client.name for client in bank_system.clients]}")

# Тестируем перевод если есть минимум 2 клиента
if len(bank_system.clients) >= 2:
    result = bank_system.transfer_money(bank_system.clients[0].name, bank_system.clients[1].name, 100)
    print(f"Перевод выполнен: {result}")
else:
    print("Нужно как минимум 2 клиента для теста перевода")


# Создаем файл истории операций если его нет
if not os.path.exists('history.json'):
    with open('history.json', 'w', encoding='utf-8') as f:
        json.dump([], f)

# Создаем главное окно
root = Tk()

# -----------------------------------------------------------------------------------------
# Функция показа истории операций
def show_history():
    history_win = Toplevel(root)
    history_win.title('История операций')
    history_win.geometry('600x400')

    # Создаем текстовое поле с прокруткой
    frame = Frame(history_win)
    frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
    
    text_area = Text(frame, width=80, height=20, font=('Arial', 10))
    scrollbar = Scrollbar(frame, orient=VERTICAL, command=text_area.yview)
    text_area.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side=RIGHT, fill=Y)
    text_area.pack(side=LEFT, fill=BOTH, expand=True)

    try:
        # Загружаем историю операций
        with open('history.json', 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if not history:
            text_area.insert(END, 'История операций пуста\n')
            return
            
        # Добавляем заголовок
        text_area.insert(END, 'Дата | Тип | Клиент | Получатель | Сумма | Баланс\n')
        text_area.insert(END, '-' * 70 + '\n')
        
        # Добавляем каждую операцию в текстовое поле
        for operation in history:
            if operation['type'] == 'Перевод':
                line = f"{operation['date']} | {operation['type']} | {operation['client']} | {operation.get('recipient_name', '')} | {operation['summa']}₽ | {operation['balance']}₽\n"
            else:
                line = f"{operation['date']} | {operation['type']} | {operation['client']} | {'—':<10} | {operation['summa']}₽ | {operation['balance']}₽\n"
            
            text_area.insert(END, line)
            
    except FileNotFoundError:
        text_area.insert(END, 'История операций пуста\n')   

# -----------------------------------------------------------------------------------------
# Функция сохранения истории операций
def save_history(summa, operation_type, sender, recipient=None):
    try:
        with open('history.json', 'r', encoding='utf-8') as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []
    
    # Проверяем тип sender (может быть dict или Client)
    if isinstance(sender, Client):
        sender_dict = sender.to_dict()
    else:
        sender_dict = sender
        
    # Создаем запись об операции
    write_data = {
        'id': sender_dict['id'],
        'client': sender_dict['name'],
        'type': operation_type,
        'summa': summa,
        'balance': sender_dict['balance'],
        'date': datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    }
    
    # Если это перевод, добавляем информацию о получателе
    if recipient and operation_type == 'Перевод':
        if isinstance(recipient, Client):
            recipient_dict = recipient.to_dict()
        else:
            recipient_dict = recipient
            
        write_data['recipient_id'] = recipient_dict['id']
        write_data['recipient_name'] = recipient_dict['name']
        write_data['recipient_balance'] = recipient_dict['balance']
    
    # Добавляем операцию в историю и сохраняем
    history.append(write_data)
    
    with open('history.json', 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

# -----------------------------------------------------------------------------------------
# Функции проверки для операций

def check_summ(summa_str):
    # Проверяем что сумма - положительное число
    try:
        summa = float(summa_str)
        if summa <= 0:
            messagebox.showerror("Ошибка", "Сумма должна быть больше 0!")
            return None
        return summa 
    except ValueError:
        messagebox.showerror("Ошибка", "Сумма должна быть числом!")
        return None

def check_str(sendler_name, summa_str, recipient_name=None):
    # Проверяем что все необходимые поля заполнены
    if recipient_name is None:
        if sendler_name == '' or summa_str == '':
            messagebox.showerror(title='Ошибка', message='Пустые строки!')
            return False
    else:
        if sendler_name == '' or summa_str == '' or recipient_name == '':
            messagebox.showerror(title='Ошибка', message='Пустые строки!')
            return False
    return True

def check_balance(client, summa):
    # Проверяем что на счету достаточно средств
    if client['balance'] < summa:
        messagebox.showerror(title='Ошибка', message='Недостаточно средств на счету!')
        return False
    return True

# -----------------------------------------------------------------------------------------
# Функции операций с деньгами

def withdrawMoney():
    # Снятие денег со счета
    sendler_name = senderInput.get()
    summa_str = summaInput.get()  
    operation_type = 'Вывод'

    # Проверяем заполнение полей
    if not check_str(sendler_name, summa_str):
        return

    # Ищем клиента
    sendler = bank_system.find_client_by_name(sendler_name)
    if sendler is None:
        return

    # Проверяем сумму
    summa = check_summ(summa_str)  
    if summa is None: 
        return
    
    # Выполняем снятие
    if sendler.withdraw(summa):
        bank_system.save_data()
        bank_system.show_operation_info(sendler, summa, 'Вывод')
        save_history(summa, operation_type, sendler)
        clear_inputs()
    else:
        messagebox.showerror('Ошибка', 'Недостаточно средств на счету!')


def depositMoney():
    # Пополнение счета
    sendler_name = senderInput.get()
    summa_str = summaInput.get()

    if not check_str(sendler_name, summa_str):
        return

    sendler = bank_system.find_client_by_name(sendler_name)
    if sendler is None:
        return
    
    summa = check_summ(summa_str)  
    if summa is None: 
        return
    
    # Выполняем пополнение
    sendler.deposit(summa)
    bank_system.save_data()
    bank_system.show_operation_info(sendler, summa, 'Пополнение')
    save_history(summa, 'Пополнение', sendler)
    clear_inputs()


def transferMoney():
    # Перевод денег другому клиенту
    sendler_name = senderInput.get()
    recipient_name = recipientInput.get()
    summa_str = summaInput.get()

    # Проверяем поля
    if not check_str(sendler_name, summa_str, recipient_name):
        return

    # Проверяем сумму
    summa = check_summ(summa_str)  
    if summa is None: 
        return
    
    # Выполняем перевод
    if bank_system.transfer_money(sendler_name, recipient_name, summa):
        sender = bank_system.find_client_by_name(sendler_name)
        recipient = bank_system.find_client_by_name(recipient_name)
        bank_system.show_operation_info(sender, summa, 'Перевод', recipient)
        save_history(summa, 'Перевод', sender, recipient)
        clear_inputs()
    else:
        sender = bank_system.find_client_by_name(sendler_name)
        if sender and sender.balance < summa:
            messagebox.showerror(title='Ошибка', message=f'Недостаточно средств для перевода, баланс:{sender.balance}')

# -----------------------------------------------------------------------------------------
# Функция админ панели

def show_admin_panel():
    # Запрашиваем пароль для доступа к админ панели
    password = simpledialog.askstring("Пароль", "Введите пароль:", show='*')
    if password != "winner":
        messagebox.showerror("Ошибка", "Неверный пароль!")
        return    

    # Создаем окно админ панели
    admin_win = Toplevel()
    admin_win.title('Админ панель - Все операции')
    admin_win.geometry('1000x400')

    main_frame = Frame(admin_win)
    main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    Label(main_frame, text='Все операции', font=('Arial', 20, 'bold')).pack(pady=15)

    tabel_frame = Frame(main_frame)
    tabel_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Создаем таблицу для отображения операций
    tabel = ttk.Treeview(tabel_frame, columns=('Date', 'Client', 'Type', 'Amount', 'Balance'), show='headings', height=15)

    tabel.heading('Date', text='Дата')
    tabel.heading('Client', text='ФИО')
    tabel.heading('Type', text='Операция')
    tabel.heading('Amount', text='Сумма')
    tabel.heading('Balance', text='Баланс')

    scrollbar = Scrollbar(tabel_frame, orient=VERTICAL, command=tabel.yview)
    tabel.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=RIGHT, fill=Y)
    tabel.pack(side=LEFT, fill=BOTH, expand=True)

    tabel.pack(fill=BOTH, expand=True,padx=10, pady=10)
    
    # Загружаем и отображаем историю операций
    try:
        with open('history.json', 'r', encoding='utf-8') as f:
            history = json.load(f)      

        for tab in history:
            balance = tab.get('balance', 'N/A') 
            tabel.insert('',END, values=(
            tab['date'],
            tab['client'],  
            tab['type'],
            f"{tab['summa']}₽",
            f"{balance}₽" if balance != 'N/A' else 'N/A'
    ))
    except FileNotFoundError:
        tabel.insert('', END, values=('', '', 'История операций пуста', '', ''))

# -----------------------------------------------------------------------------------------
# Вспомогательные функции

def clear_inputs():
    # Очищаем поля ввода
    senderInput.set('')
    recipientInput.set('')
    summaInput.delete(0, END)

def show_balance():
    # Показываем баланс выбранного клиента
    client_name = senderInput.get()
    client = bank_system.find_client_by_name(client_name)
    
    if client:
        messagebox.showinfo(title='Баланс', 
                          message=f'Клиент: {client_name}\nТекущий баланс: {client.balance}₽')
    else:
        messagebox.showerror('Ошибка!', 'Не найден клиент с таким именем')

# -----------------------------------------------------------------------------------------
# Цвета для интерфейса ВТБ
VTB_BLUE = "#002D72"
VTB_DEEPBLUE = "#032F6C"
VTB_LIGHTBLUE = '#005AA9'
VTB_WHITE = '#FFFFFF'
VTB_PURPLE = '#655B98'
VTB_GREEN = '#00A650'
VTB_BROWN = '#905809'
VTB_PINK = '#974D84'
VTB_GREY = '#F5F5F5'

# -----------------------------------------------------------------------------------------
# Создание графического интерфейса

# Настраиваем главное окно
root['bg'] = VTB_BLUE
root.title('VTB online-cassa')
root.geometry('800x600')

# Создаем верхнюю панель с логотипом
header = Frame(root, bg=VTB_BLUE)
header.pack(fill=BOTH, padx=0, pady=10)

# Загружаем и отображаем логотип
logo_image = Image.open("Vtb-logo1.png") 
logo_image = logo_image.resize((200, 80))
logo_photo = ImageTk.PhotoImage(logo_image)

logo_label = Label(header, image=logo_photo, bg=VTB_BLUE)
logo_label.pack(side=LEFT, padx=25)

# Основной фрейм
frame = Frame(root, bg=VTB_GREY)
frame.pack(fill=BOTH, expand=True, padx=0, pady=0)

# Фрейм статистики
stats_frame = Frame(frame, bg=VTB_DEEPBLUE)
stats_frame.pack(anchor='w', padx=50)

stats_labe = Label(stats_frame,bg=VTB_DEEPBLUE, text='Статистика банка 📈', font=('Arial', 14, 'bold'), fg=VTB_WHITE)
stats_labe.pack()

# Загружаем статистику операций
try:
    with open('history.json', 'r', encoding='utf-8') as f:
        history_data = json.load(f)
    total_operations = len(history_data)
except:
    total_operations = 0

# Отображаем статистику
stats_text = f"Всего клиентов: {len(bank_system.clients)}👨🏻‍💼 | Всего операций:{total_operations}👀 | Общий баланс: {sum(c.balance for c in bank_system.clients)}₽" 
Label(stats_frame, text=stats_text , font=('Arial', 12, 'bold'), fg=VTB_WHITE,bg=VTB_DEEPBLUE).pack(pady=5)

# Фрейм для операций
f_o1 = Frame(frame, bg=VTB_WHITE)
f_o1.pack(expand=True, anchor='ne', padx=20, pady = 20)

frame_oper = Frame(f_o1, bg = VTB_BLUE)
frame_oper.pack(fill=BOTH, anchor='center',padx=15, pady=15, expand=True)

# Заголовок
title = Label(header, text='Онлайн-касса', bg=VTB_BLUE, fg=VTB_WHITE, font=('Arial', 20, 'bold'))
title.pack(side=LEFT)
    
# -----------------------------------------------------------------------------------------
# Поля ввода данных

input_frame = Frame(frame_oper, bg=VTB_BLUE)
input_frame.pack(pady=20)

# Строка "От кого"
row1 = Frame(input_frame, bg=VTB_BLUE)
row1.pack(fill=X, pady=10)

Label(row1, text='От:', bg=VTB_BLUE, fg=VTB_WHITE, 
      font=('Arial', 16, 'bold'), width=8, anchor='e').pack(side=LEFT)
senderInput = ttk.Combobox(row1, values=bank_system.get_clients_names(), 
                          font=('Arial', 16), width=20)
senderInput.pack(side=LEFT, fill=X, expand=True)

# Строка "Кому"  
row2 = Frame(input_frame, bg=VTB_BLUE)
row2.pack(fill=X, pady=10)

Label(row2, text='Кому:', bg=VTB_BLUE, fg=VTB_WHITE,
      font=('Arial', 16, 'bold'), width=8, anchor='e').pack(side=LEFT)
recipientInput = ttk.Combobox(row2, values=bank_system.get_clients_names(),
                             font=('Arial', 16), width=20)
recipientInput.pack(side=LEFT, fill=X, expand=True)

# Строка "Сумма"
row3 = Frame(input_frame, bg=VTB_BLUE)
row3.pack(fill=X, pady=10)

Label(row3, text='Сумма:', bg=VTB_BLUE, fg=VTB_WHITE,
      font=('Arial', 16, 'bold'), width=8, anchor='e').pack(side=LEFT)
summaInput = Entry(row3, font=('Arial', 16), width=22)
summaInput.pack(side=LEFT, fill=X, expand=True)

# -----------------------------------------------------------------------------------------
# Кнопки операций

operation_frame = Frame(frame_oper, bg=VTB_BLUE)
operation_frame.pack(pady=10)

# Создаем кнопки для различных операций
btn_transfer = Button(operation_frame, text='Перевести💰', fg=VTB_WHITE, bg=VTB_PURPLE, command=transferMoney)
btn_transfer.grid(row=0, column=0, padx=5, pady=5)

btn_deposit = Button(operation_frame, text='Пополнить💵',fg=VTB_WHITE, bg=VTB_LIGHTBLUE, command=depositMoney)
btn_deposit.grid(row=0, column=1, padx=5, pady=5)

btn_withdraw = Button(operation_frame, text='Вывести💸',fg=VTB_WHITE, bg=VTB_BROWN, command=withdrawMoney)
btn_withdraw.grid(row=0, column=2, padx=5, pady=5)

btn_balance = Button(operation_frame, text='Баланс💲',fg=VTB_WHITE, bg=VTB_PINK, command=show_balance)
btn_balance.grid(row=0, column=3, padx=5)

btn_history = Button(operation_frame, text='История операций⌛', command=show_history)
btn_history.grid(row=0, column=4, padx=5, pady=5)

# Кнопка админ панели
border_frame = Frame(header, bg=VTB_WHITE, padx=2, pady=2)
border_frame.pack(anchor='e', padx=10, pady=10)
btn_admin_pan = Button(border_frame, text='АДМИН ПАНЕЛЬ🔑', bg=VTB_GREEN, fg='white',
                          command=show_admin_panel, bd=0, relief="flat", font=('Arial', 14, 'bold'))
btn_admin_pan.pack(side=RIGHT)

# Запускаем главный цикл приложения
root.mainloop()