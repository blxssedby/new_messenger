# client.py
import socket
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox

class MessengerClient:
    def __init__(self):
        # Новая цветовая схема (тёмная тема с акцентами)
        self.colors = {
            'bg_primary': '#1a1a2e',
            'bg_secondary': '#16213e',
            'bg_tertiary': '#0f3460',
            'accent_primary': '#e94560',
            'accent_secondary': '#533483',
            'text_primary': '#ffffff',
            'text_secondary': '#b8b8b8',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#F44336'
        }
        
        self.available_avatars = ['👦', '👧', '👨', '👩', '🧑', '👨‍💼', '👩‍💼', '🦸', '🦸‍♀️', '🐱', '🐶', '🦊', '🐼']
        self.client_socket = None
        self.username = ""
        self.avatar = "👤"
        
        self.setup_gui()
        self.setup_text_tags()  # Настраиваем теги ДО использования
    
    def setup_text_tags(self):
        # Создаем теги для форматирования текста
        if hasattr(self, 'chat_text'):
            self.chat_text.tag_configure('own_message', foreground=self.colors['accent_primary'], font=('Arial', 12, 'bold'))
            self.chat_text.tag_configure('other_message', foreground=self.colors['accent_secondary'], font=('Arial', 12, 'bold'))
    
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("🌈 Современный Мессенджер")
        self.root.configure(bg=self.colors['bg_primary'])
        self.root.geometry("800x600")
        
        self.setup_login_screen()
    
    def setup_login_screen(self):
        # Фрейм для входа
        self.login_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        self.login_frame.pack(expand=True, fill='both', padx=50, pady=50)
        
        # Заголовок
        title_label = tk.Label(
            self.login_frame,
            text="🌈 Добро пожаловать в Мессенджер",
            font=('Arial', 20, 'bold'),
            fg=self.colors['accent_primary'],
            bg=self.colors['bg_primary']
        )
        title_label.pack(pady=20)
        
        # Выбор аватара
        avatar_frame = tk.Frame(self.login_frame, bg=self.colors['bg_primary'])
        avatar_frame.pack(pady=10)
        
        tk.Label(
            avatar_frame,
            text="Выберите аватар:",
            font=('Arial', 12),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        ).pack()
        
        self.avatar_var = tk.StringVar(value="👦")
        avatar_selector = ttk.Combobox(
            avatar_frame,
            textvariable=self.avatar_var,
            values=self.available_avatars,
            state='readonly',
            font=('Arial', 16),
            width=10
        )
        avatar_selector.pack(pady=5)
        
        # Поле ввода имени
        tk.Label(
            self.login_frame,
            text="Имя пользователя:",
            font=('Arial', 12),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        ).pack(pady=5)
        
        self.username_entry = tk.Entry(
            self.login_frame,
            font=('Arial', 14),
            width=20,
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary']
        )
        self.username_entry.pack(pady=5)
        self.username_entry.bind('<Return>', lambda e: self.connect_to_server())
        
        # Поле ввода IP сервера
        tk.Label(
            self.login_frame,
            text="IP сервера:",
            font=('Arial', 12),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        ).pack(pady=5)
        
        self.server_entry = tk.Entry(
            self.login_frame,
            font=('Arial', 14),
            width=20,
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary']
        )
        self.server_entry.insert(0, "localhost")
        self.server_entry.pack(pady=5)
        self.server_entry.bind('<Return>', lambda e: self.connect_to_server())
        
        # Кнопка подключения
        connect_btn = tk.Button(
            self.login_frame,
            text="Подключиться",
            font=('Arial', 14, 'bold'),
            bg=self.colors['accent_primary'],
            fg='white',
            command=self.connect_to_server,
            width=15,
            height=2
        )
        connect_btn.pack(pady=20)
    
    def setup_chat_screen(self):
        self.login_frame.destroy()
        
        # Основной фрейм чата
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Заголовок с информацией о пользователе
        header_frame = tk.Frame(main_frame, bg=self.colors['bg_secondary'])
        header_frame.pack(fill='x', pady=(0, 10))
        
        user_info = tk.Label(
            header_frame,
            text=f"{self.avatar} {self.username}",
            font=('Arial', 14, 'bold'),
            fg=self.colors['accent_primary'],
            bg=self.colors['bg_secondary']
        )
        user_info.pack(side='left', padx=10, pady=5)
        
        online_label = tk.Label(
            header_frame,
            text="🟢 Онлайн",
            font=('Arial', 12),
            fg=self.colors['success'],
            bg=self.colors['bg_secondary']
        )
        online_label.pack(side='right', padx=10, pady=5)
        
        # Фрейм для списка пользователей и чата
        content_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        content_frame.pack(fill='both', expand=True)
        
        # Список пользователей
        users_frame = tk.Frame(content_frame, bg=self.colors['bg_secondary'], width=200)
        users_frame.pack(side='left', fill='y', padx=(0, 10))
        users_frame.pack_propagate(False)
        
        tk.Label(
            users_frame,
            text="👥 Участники",
            font=('Arial', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        ).pack(pady=10)
        
        self.users_listbox = tk.Listbox(
            users_frame,
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            font=('Arial', 11),
            border=0
        )
        self.users_listbox.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Область чата
        chat_frame = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        chat_frame.pack(side='left', fill='both', expand=True)
        
        # История сообщений
        self.chat_text = tk.Text(
            chat_frame,
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            font=('Arial', 12),
            wrap='word',
            border=0,
            padx=10,
            pady=10
        )
        self.chat_text.pack(fill='both', expand=True)
        self.chat_text.config(state='disabled')
        
        # Настраиваем теги после создания chat_text
        self.setup_text_tags()
        
        # Фрейм для ввода сообщения
        input_frame = tk.Frame(chat_frame, bg=self.colors['bg_primary'])
        input_frame.pack(fill='x', pady=(10, 0))
        
        self.message_entry = tk.Entry(
            input_frame,
            font=('Arial', 12),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary']
        )
        self.message_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.message_entry.bind('<Return>', self.send_message)
        
        send_btn = tk.Button(
            input_frame,
            text="Отправить",
            font=('Arial', 12, 'bold'),
            bg=self.colors['accent_primary'],
            fg='white',
            command=self.send_message
        )
        send_btn.pack(side='right')
    
    def connect_to_server(self):
        self.username = self.username_entry.get().strip()
        self.avatar = self.avatar_var.get()
        server_ip = self.server_entry.get().strip()
        
        if not self.username:
            messagebox.showerror("Ошибка", "Введите имя пользователя")
            return
        
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((server_ip, 5555))
            
            # Отправляем данные регистрации
            registration_data = {
                'username': self.username,
                'avatar': self.avatar
            }
            self.client_socket.send(json.dumps(registration_data).encode())
            
            self.setup_chat_screen()
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {e}")
    
    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if not message:
                    break
                    
                data = json.loads(message)
                
                if data['type'] == 'message':
                    self.display_message(
                        data['username'],
                        data['avatar'],
                        data['message'],
                        data['timestamp']
                    )
                elif data['type'] == 'avatars_update':
                    self.update_users_list(data['avatars'])
                    
            except Exception as e:
                print(f"Ошибка получения сообщения: {e}")
                break
    
    def display_message(self, username, avatar, message, timestamp):
        self.chat_text.config(state='normal')
        
        # Форматируем сообщение
        if username == self.username:
            # Свои сообщения выделяем цветом
            self.chat_text.insert('end', f"{timestamp} {avatar} Вы: ", 'own_message')
            self.chat_text.insert('end', f"{message}\n")
        else:
            self.chat_text.insert('end', f"{timestamp} {avatar} {username}: ", 'other_message')
            self.chat_text.insert('end', f"{message}\n")
        
        self.chat_text.config(state='disabled')
        self.chat_text.see('end')
    
    def update_users_list(self, avatars):
        self.users_listbox.delete(0, 'end')
        for username, avatar in avatars.items():
            self.users_listbox.insert('end', f"{avatar} {username}")
    
    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if message and self.client_socket:
            message_data = {
                'message': message
            }
            try:
                self.client_socket.send(json.dumps(message_data).encode())
                self.message_entry.delete(0, 'end')
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось отправить сообщение: {e}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    client = MessengerClient()
    client.run()