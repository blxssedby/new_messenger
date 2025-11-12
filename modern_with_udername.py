import socket
import threading
import json
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, simpledialog
from datetime import datetime

print("🚀 ЗАПУСК MODERN MESSENGER...")

class ModernMessengerClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = ""
        self.gui_done = False
        self.running = True
        
        # Современная цветовая палитра
        self.colors = {
            "primary": "#6366f1",
            "primary_dark": "#4338ca", 
            "background": "#0f172a",
            "surface": "#1e293b",
            "surface_light": "#334155",
            "text_primary": "#f8fafc",
            "text_secondary": "#cbd5e1",
            "success": "#10b981",
            "error": "#ef4444"
        }
        
    def get_user_credentials(self):
        """Получение данных пользователя перед подключением"""
        # Создаем временное окно для ввода данных
        temp_window = tk.Tk()
        temp_window.withdraw()  # Скрываем основное окно
        
        # Окно выбора имени пользователя
        self.nickname = simpledialog.askstring(
            "Выбор имени пользователя",
            "Введите ваше имя для чата:",
            parent=temp_window,
            initialvalue=f"Участник_{datetime.now().strftime('%H%M')}"
        )
        
        if not self.nickname:
            self.nickname = f"Участник_{datetime.now().strftime('%H%M%S')}"
        
        # Окно ввода данных сервера
        host = simpledialog.askstring(
            "Подключение к серверу",
            "Введите адрес сервера:",
            parent=temp_window,
            initialvalue="localhost"
        )
        if not host:
            host = "localhost"
            
        port = simpledialog.askinteger(
            "Подключение к серверу", 
            "Введите порт сервера:",
            parent=temp_window,
            initialvalue=5555,
            minvalue=1000,
            maxvalue=65535
        )
        if not port:
            port = 5555
            
        temp_window.destroy()
        
        return host, port
    
    def connect_to_server(self, host='localhost', port=5555):
        """Подключение к серверу"""
        try:
            print(f"🔗 Подключаемся к {host}:{port}...")
            print(f"👤 Ваше имя: {self.nickname}")
            
            self.client.connect((host, port))
            message = self.client.recv(1024).decode('utf-8')
            
            if message == "NICK":
                self.client.send(self.nickname.encode('utf-8'))
                print("✅ Имя отправлено на сервер")
                return True
            else:
                print("❌ Неожиданный ответ от сервера")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            messagebox.showerror(
                "Ошибка подключения", 
                f"Не удалось подключиться к серверу:\n{host}:{port}\n\n"
                f"Ошибка: {e}\n\n"
                "Проверьте:\n"
                "• Запущен ли сервер\n"
                "• Правильность адреса и порта\n"
                "• Настройки сети"
            )
            return False
    
    def create_ui(self):
        """Создание современного интерфейса"""
        self.window = tk.Tk()
        self.window.title(f"💬 Modern Messenger — {self.nickname}")
        self.window.geometry("1000x700")
        self.window.configure(bg=self.colors["background"])
        self.window.minsize(900, 600)
        
        # Верхняя панель
        self.create_header()
        
        # Основной контент
        self.create_content()
        
        return self.window
    
    def create_header(self):
        """Создание верхней панели"""
        header = tk.Frame(self.window, bg=self.colors["primary"], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Заголовок и информация о пользователе
        title_frame = tk.Frame(header, bg=self.colors["primary"])
        title_frame.pack(fill=tk.X, padx=30, pady=15)
        
        title_label = tk.Label(
            title_frame,
            text="💬 Modern Messenger",
            bg=self.colors["primary"],
            fg=self.colors["text_primary"],
            font=("Arial", 18, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # Информация о пользователе
        user_info = tk.Label(
            title_frame,
            text=f"👤 {self.nickname}",
            bg=self.colors["primary"],
            fg=self.colors["text_primary"],
            font=("Arial", 11)
        )
        user_info.pack(side=tk.RIGHT, padx=(0, 20))
        
        # Статус
        status_frame = tk.Frame(header, bg=self.colors["primary"])
        status_frame.pack(side=tk.RIGHT, padx=30, pady=15)
        
        self.status_indicator = tk.Label(
            status_frame,
            text="●",
            fg=self.colors["success"],
            bg=self.colors["primary"],
            font=("Arial", 14)
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 8))
        
        self.status_label = tk.Label(
            status_frame,
            text="В сети",
            bg=self.colors["primary"],
            fg=self.colors["text_primary"],
            font=("Arial", 11)
        )
        self.status_label.pack(side=tk.RIGHT)
    
    def create_content(self):
        """Создание основной области контента"""
        # Создаем вкладки
        tab_control = ttk.Notebook(self.window)
        
        # Стилизация вкладок
        style = ttk.Style()
        style.configure("TNotebook", background=self.colors["background"])
        style.configure("TNotebook.Tab", 
                       background=self.colors["surface"],
                       foreground=self.colors["text_primary"],
                       padding=[15, 8])
        
        # Вкладки
        chat_tab = ttk.Frame(tab_control)
        users_tab = ttk.Frame(tab_control)
        profile_tab = ttk.Frame(tab_control)  # Новая вкладка профиля
        
        tab_control.add(chat_tab, text="💬 Чат")
        tab_control.add(users_tab, text="👥 Участники")
        tab_control.add(profile_tab, text="👤 Профиль")
        
        tab_control.pack(expand=True, fill='both', padx=15, pady=15)
        
        # Настройка вкладок
        self.setup_chat_tab(chat_tab)
        self.setup_users_tab(users_tab)
        self.setup_profile_tab(profile_tab)
    
    def setup_chat_tab(self, parent):
        """Настройка вкладки чата"""
        # Область сообщений
        self.chat_area = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            bg=self.colors["surface"],
            fg=self.colors["text_primary"],
            font=("Arial", 12),
            state=tk.DISABLED,
            padx=20,
            pady=20,
            relief=tk.FLAT
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Простые стили сообщений
        self.chat_area.tag_config("own", foreground="#4CAF50", background="#1e3a28")
        self.chat_area.tag_config("other", foreground="#ffffff", background="#2d3748") 
        self.chat_area.tag_config("system", foreground="#FF9800", justify="center")
        self.chat_area.tag_config("username", foreground="#6366f1", font=("Arial", 10, "bold"))
        
        # Панель ввода
        input_frame = tk.Frame(parent, bg=self.colors["background"])
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Кнопка смайликов
        emoji_btn = tk.Button(
            input_frame,
            text="😊",
            command=self.show_emojis,
            bg=self.colors["surface_light"],
            fg=self.colors["text_primary"],
            font=("Arial", 14),
            relief=tk.FLAT,
            width=3
        )
        emoji_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Поле ввода
        self.message_entry = tk.Entry(
            input_frame,
            font=("Arial", 13),
            bg=self.colors["surface_light"],
            fg=self.colors["text_primary"],
            insertbackground=self.colors["text_primary"],
            relief=tk.FLAT
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=8, ipady=8)
        self.message_entry.bind("<Return>", self.send_message)
        
        # Кнопка отправки
        self.send_btn = tk.Button(
            input_frame,
            text="Отправить",
            command=self.send_message,
            bg=self.colors["primary"],
            fg=self.colors["text_primary"],
            font=("Arial", 11, "bold"),
            relief=tk.FLAT,
            padx=20
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Анимация кнопки
        self.send_btn.bind("<Enter>", lambda e: self.send_btn.config(bg=self.colors["primary_dark"]))
        self.send_btn.bind("<Leave>", lambda e: self.send_btn.config(bg=self.colors["primary"]))
        
        # Приветственное сообщение
        self.show_welcome_message()
    
    def setup_users_tab(self, parent):
        """Настройка вкладки участников"""
        # Заголовок
        title_label = tk.Label(
            parent,
            text="👥 Активные участники",
            bg=self.colors["background"],
            fg=self.colors["text_primary"],
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # Список пользователей
        users_frame = tk.Frame(parent, bg=self.colors["surface"])
        users_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.users_list = tk.Listbox(
            users_frame,
            bg=self.colors["surface"],
            fg=self.colors["text_primary"],
            font=("Arial", 12),
            selectbackground=self.colors["primary"],
            relief=tk.FLAT
        )
        self.users_list.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Добавляем текущего пользователя
        self.update_users_list()
        
        # Статистика
        stats_frame = tk.Frame(parent, bg=self.colors["background"])
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        stats_text = f"""📊 Статистика:
• Ваше имя: {self.nickname}
• Участников: 1
• Статус: В сети
• Время: {datetime.now().strftime('%H:%M')}"""
        
        stats_label = tk.Label(
            stats_frame,
            text=stats_text,
            bg=self.colors["background"],
            fg=self.colors["text_secondary"],
            font=("Arial", 10),
            justify=tk.LEFT
        )
        stats_label.pack(anchor=tk.W)
    
    def setup_profile_tab(self, parent):
        """Настройка вкладки профиля пользователя"""
        # Заголовок
        title_label = tk.Label(
            parent,
            text="👤 Ваш профиль",
            bg=self.colors["background"],
            fg=self.colors["text_primary"],
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=30)
        
        # Карточка профиля
        profile_card = tk.Frame(parent, bg=self.colors["surface"])
        profile_card.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # Аватар (заглушка)
        avatar_frame = tk.Frame(profile_card, bg=self.colors["surface"])
        avatar_frame.pack(pady=20)
        
        avatar_label = tk.Label(
            avatar_frame,
            text="👤",
            bg=self.colors["surface"],
            fg=self.colors["primary"],
            font=("Arial", 48)
        )
        avatar_label.pack()
        
        # Информация о пользователе
        info_frame = tk.Frame(profile_card, bg=self.colors["surface"])
        info_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Имя пользователя
        name_frame = tk.Frame(info_frame, bg=self.colors["surface"])
        name_frame.pack(fill=tk.X, pady=10)
        
        name_title = tk.Label(
            name_frame,
            text="Имя в чате:",
            bg=self.colors["surface"],
            fg=self.colors["text_secondary"],
            font=("Arial", 11),
            width=15,
            anchor="w"
        )
        name_title.pack(side=tk.LEFT)
        
        self.name_display = tk.Label(
            name_frame,
            text=self.nickname,
            bg=self.colors["surface"],
            fg=self.colors["text_primary"],
            font=("Arial", 12, "bold")
        )
        self.name_display.pack(side=tk.LEFT)
        
        # Кнопка смены имени
        change_name_btn = tk.Button(
            info_frame,
            text="✏️ Сменить имя",
            command=self.change_username,
            bg=self.colors["primary"],
            fg=self.colors["text_primary"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        change_name_btn.pack(pady=20)
        
        # Информация о подключении
        conn_frame = tk.Frame(profile_card, bg=self.colors["surface"])
        conn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        conn_text = f"""🌐 Информация о подключении:
        
• Имя пользователя: {self.nickname}
• Статус: Подключен к серверу
• Время в сети: {datetime.now().strftime('%H:%M')}
• ID сессии: {id(self)}"""
        
        conn_label = tk.Label(
            conn_frame,
            text=conn_text,
            bg=self.colors["surface"],
            fg=self.colors["text_secondary"],
            font=("Arial", 10),
            justify=tk.LEFT
        )
        conn_label.pack(anchor=tk.W)
    
    def change_username(self):
        """Смена имени пользователя"""
        new_name = simpledialog.askstring(
            "Смена имени",
            "Введите новое имя:",
            parent=self.window,
            initialvalue=self.nickname
        )
        
        if new_name and new_name.strip() and new_name != self.nickname:
            old_name = self.nickname
            self.nickname = new_name.strip()
            
            # Обновляем отображение
            self.window.title(f"💬 Modern Messenger — {self.nickname}")
            self.name_display.config(text=self.nickname)
            
            # Отправляем системное сообщение о смене имени
            try:
                system_message = f"{old_name} сменил(а) имя на {self.nickname}"
                self.client.send(system_message.encode('utf-8'))
            except:
                messagebox.showwarning("Внимание", "Не удалось уведомить других пользователей о смене имени")
            
            messagebox.showinfo("Успех", f"Имя изменено на: {self.nickname}")
    
    def update_users_list(self):
        """Обновление списка пользователей"""
        if hasattr(self, 'users_list'):
            self.users_list.delete(0, tk.END)
            self.users_list.insert(tk.END, f"👤 {self.nickname} (Вы)")
            self.users_list.insert(tk.END, "🟢 Другие участники появятся здесь...")
    
    def show_emojis(self):
        """Показать смайлики"""
        emoji_window = tk.Toplevel(self.window)
        emoji_window.title("Смайлики")
        emoji_window.geometry("350x200")
        emoji_window.configure(bg=self.colors["surface"])
        
        # Смайлики
        emojis = ["😊", "😂", "🥰", "😍", "🤩", "😎", "🤔", "😢", "🎉", "❤️"]
        
        for i, emoji in enumerate(emojis):
            btn = tk.Button(
                emoji_window,
                text=emoji,
                command=lambda e=emoji: self.add_emoji(e, emoji_window),
                bg=self.colors["surface_light"],
                fg=self.colors["text_primary"],
                font=("Arial", 16),
                relief=tk.FLAT
            )
            btn.grid(row=i//5, column=i%5, padx=5, pady=5)
    
    def add_emoji(self, emoji, window):
        """Добавить смайлик"""
        self.message_entry.insert(tk.END, emoji)
        window.destroy()
    
    def show_welcome_message(self):
        """Показать приветственное сообщение"""
        self.chat_area.config(state=tk.NORMAL)
        welcome = f"""
{'=' * 50}
    🎉 ДОБРО ПОЖАЛОВАТЬ, {self.nickname}!
    💬 Modern Messenger готов к работе
    🕒 Время подключения: {datetime.now().strftime('%H:%M')}
{'=' * 50}


"""
        self.chat_area.insert(tk.END, welcome, "system")
        self.chat_area.config(state=tk.DISABLED)
    
    def send_message(self, event=None):
        """Отправка сообщения"""
        message = self.message_entry.get().strip()
        if message:
            try:
                self.client.send(message.encode('utf-8'))
                self.message_entry.delete(0, tk.END)
            except:
                messagebox.showerror("Ошибка", "Не удалось отправить сообщение")
                self.status_label.config(text="Отключен")
                self.status_indicator.config(fg=self.colors["error"])
    
    def receive_messages(self):
        """Получение сообщений"""
        while self.running:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message:
                    data = json.loads(message)
                    self.display_message(data)
            except:
                if self.running:
                    self.show_system_message("❌ Отключен от сервера")
                break
    
    def display_message(self, message_data):
        """Отображение сообщения"""
        if self.gui_done:
            self.chat_area.config(state=tk.NORMAL)
            
            sender = message_data["sender"]
            message = message_data["message"]
            time = message_data["timestamp"]
            
            if sender:
                if sender == self.nickname:
                    self.chat_area.insert(tk.END, f"[{time}] ", "system")
                    self.chat_area.insert(tk.END, "Вы: ", "username")
                    self.chat_area.insert(tk.END, f"{message}\n", "own")
                else:
                    self.chat_area.insert(tk.END, f"[{time}] ", "system")
                    self.chat_area.insert(tk.END, f"{sender}: ", "username")
                    self.chat_area.insert(tk.END, f"{message}\n", "other")
            else:
                self.chat_area.insert(tk.END, f"⚡ {message}\n", "system")
            
            self.chat_area.config(state=tk.DISABLED)
            self.chat_area.see(tk.END)
    
    def show_system_message(self, message):
        """Показать системное сообщение"""
        if self.gui_done:
            self.chat_area.config(state=tk.NORMAL)
            self.chat_area.insert(tk.END, f"⚡ {message}\n", "system")
            self.chat_area.config(state=tk.DISABLED)
            self.chat_area.see(tk.END)
    
    def gui_loop(self):
        """Запуск интерфейса"""
        print("🎨 Создаем интерфейс...")
        self.window = self.create_ui()
        
        self.gui_done = True
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.message_entry.focus()
        
        # Запуск потока для получения сообщений
        thread = threading.Thread(target=self.receive_messages)
        thread.daemon = True
        thread.start()
        
        print("✅ Интерфейс создан! Запускаем...")
        self.window.mainloop()
    
    def on_closing(self):
        """Закрытие приложения"""
        self.running = False
        try:
            self.client.close()
        except:
            pass
        self.window.destroy()

def main():
    print("=" * 50)
    print("🎮 MODERN MESSENGER С ВЫБОРОМ ИМЕНИ")
    print("=" * 50)
    
    client = ModernMessengerClient()
    
    # Получаем данные пользователя
    host, port = client.get_user_credentials()
    
    if client.connect_to_server(host, port):
        print("✅ Подключено! Запускаем интерфейс...")
        client.gui_loop()
    else:
        print("❌ Ошибка подключения")
        input("Нажмите Enter...")

if __name__ == "__main__":
    main()