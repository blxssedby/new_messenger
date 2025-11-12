import socket
import threading
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import time
from datetime import datetime
import base64
from PIL import Image, ImageTk
import io

class TelegramClient:
    def __init__(self):
        self.host = 'localhost'
        self.port = 5555
        self.socket = None
        self.username = None
        self.current_chat = "general"
        self.connected = False
        self.selected_avatar = "👤"
        self.message_widgets = {}  # Хранит связь между ID сообщения и виджетами
        
        self.chats = {
            "general": "💬 Общий",
            "random": "🎲 Случайности", 
            "help": "❓ Помощь",
            "offline": "📴 Оффлайн",
            "fireplace": "🔥 Камин",
            "work": "💼 Работа",
            "friends": "👥 Друзья",
            "music": "🎵 Музыка",
            "games": "🎮 Игры",
            "programming": "💻 Программирование"
        }
        
        self.avatars = [
            "👤", "👨", "👩", "🧑", "👦", "👧", "🧒", "👨‍💼", "👩‍💼", 
            "👨‍🎓", "👩‍🎓", "👨‍🔬", "👩‍🔬", "👨‍💻", "👩‍💻", "👨‍🎤", "👩‍🎤",
            "🦊", "🐱", "🐶", "🐼", "🐨", "🐯", "🦁", "🐮", "🐷",
            "🐔", "🐧", "🐦", "🦅", "🦉", "🦇", "🐺", "🐗", "🐴",
            "🦄", "🐝", "🐛", "🦋", "🐌", "🐞", "🐢", "🐍", "🦎",
            "🐙", "🦑", "🦐", "🦀", "🐡", "🐠", "🐟", "🐬", "🐳",
            "🐊", "🦖", "🦕", "🐅", "🐆", "🦓", "🦍", "🦧", "🐘",
            "🦛", "🦏", "🐪", "🐫", "🦒", "🦘", "🐃", "🐂", "🐄",
            "🐎", "🐖", "🐏", "🐑", "🦙", "🐐", "🦌", "🐕", "🐩",
            "🐈", "🐓", "🦃", "🦚", "🦜", "🦢", "🦩", "🐇", "🦝",
            "🦨", "🦡", "🦦", "🦥", "🐁", "🐀", "🦔", "🌚", "🌝",
            "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊",
            "😇", "🙂", "🙃", "😉", "😌", "😍", "🥰", "😘", "😗",
            "😙", "😚", "😋", "😛", "😝", "😜", "🤪", "🤨", "🧐",
            "🤓", "😎", "🤩", "🥳", "😏", "😒", "😞", "😔", "😟",
            "😕", "🙁", "☹️", "😣", "😖", "😫", "😩", "🥺", "😢",
            "😭", "😤", "😠", "😡", "🤬", "🤯", "😳", "🥵", "🥶",
            "😱", "😨", "😰", "😥", "😓", "🤗", "🤔", "🤭", "🤫",
            "🤥", "😶", "😐", "😑", "😬", "🙄", "😯", "😦", "😧",
            "😮", "😲", "🥱", "😴", "🤤", "😪", "😵", "🤐", "🥴",
            "🤢", "🤮", "🤧", "😷", "🤒", "🤕", "🤑", "🤠", "😈",
            "👿", "👹", "👺", "🤡", "💩", "👻", "💀", "☠️", "👽",
            "👾", "🤖", "🎃", "😺", "😸", "😹", "😻", "😼", "😽",
            "🙀", "😿", "😾"
        ]
        
        self.setup_gui()
        
    def setup_gui(self):
        """Настройка графического интерфейса в стиле Telegram"""
        self.root = tk.Tk()
        self.root.title("Telegram Messenger")
        self.root.geometry("900x750")
        self.root.configure(bg='#1e1e1e')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Стили
        self.setup_styles()
        
        self.setup_login_screen()
        
    def setup_styles(self):
        """Настройка стилей для красивого интерфейса"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Modern.TButton', 
                       background='#0088cc',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 10),
                       font=('Segoe UI', 10, 'bold'))
        
        style.map('Modern.TButton',
                 background=[('active', '#0077b3'),
                           ('pressed', '#006699')])
        
        style.configure('Modern.TEntry',
                       fieldbackground='#2d2d2d',
                       foreground='white',
                       borderwidth=1,
                       relief='flat')
        
        style.configure('Modern.TCombobox',
                       fieldbackground='#2d2d2d',
                       background='#2d2d2d',
                       foreground='white',
                       arrowcolor='white')
        
        style.configure('Modern.TFrame', background='#1e1e1e')
        
    def setup_login_screen(self):
        """Красивый экран входа с выбором аватара"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Основной фрейм
        main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=30)
        
        # Заголовок
        title_label = tk.Label(main_frame, 
                              text="Telegram",
                              font=('Segoe UI', 32, 'bold'),
                              fg='#0088cc',
                              bg='#1e1e1e')
        title_label.pack(pady=(30, 10))
        
        subtitle_label = tk.Label(main_frame,
                                text="Войдите в свой аккаунт",
                                font=('Segoe UI', 12),
                                fg='#888888',
                                bg='#1e1e1e')
        subtitle_label.pack(pady=(0, 30))
        
        # Фрейм для формы
        form_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        form_frame.pack(fill=tk.X, pady=20)
        
        # Выбор аватара
        tk.Label(form_frame, 
                text="Выберите аватар",
                font=('Segoe UI', 10),
                fg='#cccccc',
                bg='#1e1e1e').pack(anchor='w', pady=(0, 10))
        
        avatar_frame = tk.Frame(form_frame, bg='#1e1e1e')
        avatar_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Показываем первые 12 аватаров для выбора
        self.avatar_buttons = []
        for i, avatar in enumerate(self.avatars[:12]):
            btn = tk.Button(avatar_frame,
                          text=avatar,
                          font=('Segoe UI', 16),
                          fg='#cccccc',
                          bg='#2d2d2d',
                          activebackground='#3d3d3d',
                          borderwidth=2,
                          relief='solid' if avatar == self.selected_avatar else 'flat',
                          cursor='hand2',
                          command=lambda a=avatar: self.select_avatar(a))
            btn.pack(side=tk.LEFT, padx=5)
            self.avatar_buttons.append(btn)
        
        # Поле ввода имени
        tk.Label(form_frame, 
                text="Ваше имя",
                font=('Segoe UI', 10),
                fg='#cccccc',
                bg='#1e1e1e').pack(anchor='w', pady=(0, 5))
        
        self.username_entry = ttk.Entry(form_frame, 
                                      style='Modern.TEntry',
                                      font=('Segoe UI', 11),
                                      width=30)
        self.username_entry.pack(fill=tk.X, pady=(0, 20))
        self.username_entry.bind('<Return>', lambda e: self.connect_to_server())
        
        # Выбор чата
        tk.Label(form_frame,
                text="Выберите чат",
                font=('Segoe UI', 10),
                fg='#cccccc',
                bg='#1e1e1e').pack(anchor='w', pady=(0, 5))
        
        self.chat_var = tk.StringVar(value="general")
        chat_combo = ttk.Combobox(form_frame, 
                                 textvariable=self.chat_var, 
                                 values=list(self.chats.keys()),
                                 style='Modern.TCombobox',
                                 state="readonly",
                                 font=('Segoe UI', 10))
        chat_combo.pack(fill=tk.X, pady=(0, 30))
        
        # Кнопка подключения
        connect_btn = ttk.Button(form_frame, 
                                text="ПОДКЛЮЧИТЬСЯ",
                                style='Modern.TButton',
                                command=self.connect_to_server)
        connect_btn.pack(fill=tk.X, pady=10)
        
        # Статус
        self.status_label = tk.Label(form_frame, 
                                   text=f"⚪ Не подключено | Аватар: {self.selected_avatar}",
                                   font=('Segoe UI', 9),
                                   fg='#ff4444',
                                   bg='#1e1e1e')
        self.status_label.pack(pady=20)
        
        self.username_entry.focus()
        
    def select_avatar(self, avatar):
        """Выбор аватара"""
        self.selected_avatar = avatar
        self.status_label.config(text=f"⚪ Не подключено | Аватар: {self.selected_avatar}")
        
        # Обновляем внешний вид кнопок аватаров
        for btn in self.avatar_buttons:
            if btn['text'] == avatar:
                btn.config(relief='solid', fg='#0088cc')
            else:
                btn.config(relief='flat', fg='#cccccc')
        
    def setup_chat_interface(self):
        """Современный интерфейс чата в стиле Telegram"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Основной контейнер
        main_container = ttk.Frame(self.root, style='Modern.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Боковая панель с чатами
        sidebar_frame = ttk.Frame(main_container, style='Modern.TFrame', width=200)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
        sidebar_frame.pack_propagate(False)
        
        # Заголовок боковой панели
        sidebar_header = tk.Frame(sidebar_frame, bg='#0088cc', height=80)
        sidebar_header.pack(fill=tk.X)
        sidebar_header.pack_propagate(False)
        
        tk.Label(sidebar_header, 
                text=f"{self.selected_avatar} {self.username}",
                font=('Segoe UI', 12, 'bold'),
                fg='white',
                bg='#0088cc').pack(expand=True, pady=10)
        
        # Кнопка смены аватара
        change_avatar_btn = tk.Button(sidebar_header,
                                    text="🔄 Сменить аватар",
                                    font=('Segoe UI', 9),
                                    fg='white',
                                    bg='#0077b3',
                                    activebackground='#006699',
                                    borderwidth=0,
                                    cursor='hand2',
                                    command=self.show_avatar_selector)
        change_avatar_btn.pack(pady=(0, 10))
        
        # Список чатов
        chats_frame = tk.Frame(sidebar_frame, bg='#2d2d2d')
        chats_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(chats_frame,
                text="Чаты",
                font=('Segoe UI', 11, 'bold'),
                fg='#cccccc',
                bg='#2d2d2d').pack(anchor='w', pady=(15, 10), padx=15)
        
        # Кнопки чатов
        for chat_key, chat_name in self.chats.items():
            chat_btn = tk.Button(chats_frame,
                               text=f"  {chat_name}",
                               font=('Segoe UI', 10),
                               fg='#cccccc' if chat_key != self.current_chat else '#0088cc',
                               bg='#2d2d2d',
                               activebackground='#3d3d3d',
                               activeforeground='white',
                               borderwidth=0,
                               anchor='w',
                               cursor='hand2',
                               command=lambda c=chat_key: self.change_chat_ui(c))
            chat_btn.pack(fill=tk.X, padx=5, pady=2)
        
        # Основная область чата
        chat_frame = ttk.Frame(main_container, style='Modern.TFrame')
        chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Заголовок чата
        chat_header = tk.Frame(chat_frame, bg='#1e1e1e', height=60)
        chat_header.pack(fill=tk.X)
        chat_header.pack_propagate(False)
        
        self.chat_title_label = tk.Label(chat_header,
                                       text=self.chats[self.current_chat],
                                       font=('Segoe UI', 14, 'bold'),
                                       fg='white',
                                       bg='#1e1e1e')
        self.chat_title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Кнопки управления
        control_frame = tk.Frame(chat_header, bg='#1e1e1e')
        control_frame.pack(side=tk.RIGHT, padx=20, pady=20)
        
        users_btn = tk.Button(control_frame,
                            text="👥",
                            font=('Segoe UI', 12),
                            fg='#0088cc',
                            bg='#1e1e1e',
                            borderwidth=0,
                            cursor='hand2',
                            command=self.request_users)
        users_btn.pack(side=tk.LEFT, padx=5)
        
        disconnect_btn = tk.Button(control_frame,
                                 text="🔌",
                                 font=('Segoe UI', 12),
                                 fg='#ff4444',
                                 bg='#1e1e1e',
                                 borderwidth=0,
                                 cursor='hand2',
                                 command=self.disconnect)
        disconnect_btn.pack(side=tk.LEFT, padx=5)
        
        # Область сообщений
        messages_container = tk.Frame(chat_frame, bg='#1e1e1e')
        messages_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Создаем Canvas и Scrollbar для сообщений
        self.messages_canvas = tk.Canvas(messages_container, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(messages_container, orient="vertical", command=self.messages_canvas.yview)
        self.messages_frame = tk.Frame(self.messages_canvas, bg='#1e1e1e')
        
        self.messages_frame.bind("<Configure>", lambda e: self.messages_canvas.configure(
            scrollregion=self.messages_canvas.bbox("all")))
        
        self.messages_canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")
        self.messages_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.messages_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Привязываем скролл колесиком мыши
        self.messages_canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Панель ввода сообщения
        input_frame = tk.Frame(chat_frame, bg='#2d2d2d', height=70)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        input_frame.pack_propagate(False)
        
        self.message_entry = tk.Entry(input_frame,
                                    font=('Segoe UI', 11),
                                    bg='#2d2d2d',
                                    fg='white',
                                    insertbackground='white',
                                    borderwidth=0,
                                    relief='flat')
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 10), pady=15)
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        
        send_btn = tk.Button(input_frame,
                           text="➤",
                           font=('Segoe UI', 14, 'bold'),
                           fg='#0088cc',
                           bg='#2d2d2d',
                           activebackground='#3d3d3d',
                           activeforeground='#0088cc',
                           borderwidth=0,
                           cursor='hand2',
                           command=self.send_message)
        send_btn.pack(side=tk.RIGHT, padx=15, pady=15)
        
        self.message_entry.focus()
        
    def show_avatar_selector(self):
        """Окно выбора аватара"""
        avatar_window = tk.Toplevel(self.root)
        avatar_window.title("Выбор аватара")
        avatar_window.geometry("400x500")
        avatar_window.configure(bg='#1e1e1e')
        avatar_window.transient(self.root)
        avatar_window.grab_set()
        
        tk.Label(avatar_window, 
                text="Выберите аватар",
                font=('Segoe UI', 16, 'bold'),
                fg='white',
                bg='#1e1e1e').pack(pady=20)
        
        # Фрейм для аватаров с прокруткой
        canvas = tk.Canvas(avatar_window, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(avatar_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1e1e1e')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Отображаем все аватары
        row, col = 0, 0
        for i, avatar in enumerate(self.avatars):
            btn = tk.Button(scrollable_frame,
                          text=avatar,
                          font=('Segoe UI', 20),
                          fg='#cccccc' if avatar != self.selected_avatar else '#0088cc',
                          bg='#2d2d2d',
                          activebackground='#3d3d3d',
                          borderwidth=2,
                          relief='solid' if avatar == self.selected_avatar else 'flat',
                          cursor='hand2',
                          command=lambda a=avatar: self.change_avatar(a, avatar_window))
            btn.grid(row=row, column=col, padx=5, pady=5)
            
            col += 1
            if col >= 6:  # 6 аватаров в строке
                col = 0
                row += 1
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")
        
    def change_avatar(self, new_avatar, window):
        """Смена аватара"""
        self.selected_avatar = new_avatar
        window.destroy()
        
        # Отправляем запрос на сервер
        if self.connected:
            avatar_data = {
                "action": "change_avatar",
                "avatar": new_avatar
            }
            try:
                self.socket.send(json.dumps(avatar_data).encode('utf-8'))
            except:
                pass
                
    def _on_mousewheel(self, event):
        """Обработка скролла мыши"""
        self.messages_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def create_message_widget(self, message_data, is_my_message=False):
        """Создание виджета сообщения"""
        message_frame = tk.Frame(self.messages_frame, bg='#1e1e1e')
        message_frame.pack(fill=tk.X, pady=5)
        
        # Аватар и содержимое
        content_frame = tk.Frame(message_frame, bg='#1e1e1e')
        content_frame.pack(fill=tk.X, padx=10)
        
        # Аватар
        avatar_label = tk.Label(content_frame,
                              text=message_data.get('avatar', '👤'),
                              font=('Segoe UI', 14),
                              bg='#1e1e1e',
                              fg='#0088cc')
        avatar_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Текст сообщения
        text_frame = tk.Frame(content_frame, bg='#1e1e1e')
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Имя пользователя и время
        username_label = tk.Label(text_frame,
                                text=message_data['username'],
                                font=('Segoe UI', 10, 'bold'),
                                fg='#0088cc' if is_my_message else '#00c853',
                                bg='#1e1e1e',
                                anchor='w')
        username_label.pack(anchor='w')
        
        timestamp = datetime.fromtimestamp(message_data['timestamp']).strftime('%H:%M')
        time_label = tk.Label(text_frame,
                            text=timestamp,
                            font=('Segoe UI', 8),
                            fg='#757575',
                            bg='#1e1e1e')
        time_label.pack(anchor='w')
        
        # Текст сообщения
        message_label = tk.Label(text_frame,
                               text=message_data['message'],
                               font=('Segoe UI', 10),
                               fg='white',
                               bg='#1e1e1e',
                               justify='left',
                               wraplength=400)
        message_label.pack(anchor='w', pady=(2, 0))
        
        # Кнопка удаления для своих сообщений
        if is_my_message and message_data.get('can_delete', True):
            delete_btn = tk.Button(text_frame,
                                 text="🗑️",
                                 font=('Segoe UI', 8),
                                 fg='#ff4444',
                                 bg='#1e1e1e',
                                 borderwidth=0,
                                 cursor='hand2',
                                 command=lambda: self.delete_message(message_data['id']))
            delete_btn.pack(anchor='w', pady=(5, 0))
        
        # Сохраняем связь ID сообщения с виджетами
        self.message_widgets[message_data['id']] = {
            'frame': message_frame,
            'content_frame': content_frame,
            'text_frame': text_frame,
            'username_label': username_label,
            'time_label': time_label,
            'message_label': message_label
        }
        
        # Прокрутка вниз
        self.messages_canvas.update_idletasks()
        self.messages_canvas.yview_moveto(1.0)
        
    def delete_message(self, message_id):
        """Удаление сообщения"""
        if self.connected:
            delete_data = {
                "action": "delete_message",
                "message_id": message_id
            }
            try:
                self.socket.send(json.dumps(delete_data).encode('utf-8'))
            except:
                messagebox.showerror("Ошибка", "Не удалось удалить сообщение")
                
    def remove_message_widget(self, message_id):
        """Удаление виджета сообщения из интерфейса"""
        if message_id in self.message_widgets:
            widgets = self.message_widgets[message_id]
            widgets['frame'].destroy()
            del self.message_widgets[message_id]
        
    def connect_to_server(self):
        """Подключение к серверу"""
        if self.connected:
            return
            
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Ошибка", "Введите имя пользователя")
            return
            
        if len(username) > 50:
            messagebox.showerror("Ошибка", "Имя пользователя слишком длинное (макс. 50 символов)")
            return
            
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            
            self.username = username
            self.current_chat = self.chat_var.get()
            
            # Отправка данных для входа
            login_data = {
                "action": "login",
                "username": self.username,
                "chat": self.current_chat,
                "avatar": self.selected_avatar
            }
            self.socket.send(json.dumps(login_data).encode('utf-8'))
            
            # Запуск потока для получения сообщений
            receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            receive_thread.start()
            
            print(f"✅ Успешно подключен как {self.username}")
            self.status_label.config(text="🟢 Подключено", fg='#00c853')
            self.setup_chat_interface()
            
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            messagebox.showerror("Ошибка", f"Не удалось подключиться к серверу:\n{e}")
            if self.socket:
                self.socket.close()
                self.socket = None
            self.connected = False
            self.status_label.config(text="🔴 Ошибка подключения", fg='#ff4444')
            
    def disconnect(self):
        """Отключение от сервера"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            
        self.message_widgets = {}
        self.setup_login_screen()
        
    def change_chat_ui(self, new_chat):
        """Смена чата через UI"""
        if new_chat != self.current_chat and self.connected:
            self.current_chat = new_chat
            self.chat_title_label.config(text=self.chats[new_chat])
            
            # Очищаем сообщения
            for widget in self.messages_frame.winfo_children():
                widget.destroy()
            self.message_widgets = {}
            
            change_data = {
                "action": "change_chat",
                "chat": new_chat
            }
            try:
                self.socket.send(json.dumps(change_data).encode('utf-8'))
            except:
                pass
                
    def request_users(self):
        """Запрос списка пользователей"""
        if self.connected:
            users_data = {
                "action": "get_users"
            }
            try:
                self.socket.send(json.dumps(users_data).encode('utf-8'))
            except:
                pass
                
    def send_message(self):
        """Отправка сообщения"""
        if not self.connected:
            messagebox.showerror("Ошибка", "Не подключено к серверу")
            return
            
        message = self.message_entry.get().strip()
        if not message:
            return
            
        message_data = {
            "action": "message",
            "message": message
        }
        
        try:
            self.socket.send(json.dumps(message_data).encode('utf-8'))
            self.message_entry.delete(0, tk.END)
        except Exception as e:
            print(f"❌ Ошибка отправки сообщения: {e}")
            messagebox.showerror("Ошибка", "Не удалось отправить сообщение")
            
    def receive_messages(self):
        """Получение сообщений от сервера"""
        while self.connected:
            try:
                message = self.socket.recv(1024).decode('utf-8')
                if not message:
                    break
                    
                data = json.loads(message)
                self.display_message(data)
                
            except json.JSONDecodeError:
                print("❌ Получено неверное JSON сообщение")
            except ConnectionAbortedError:
                break
            except Exception as e:
                print(f"❌ Ошибка получения сообщений: {e}")
                break
                
        if self.connected:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", "Соединение с сервером потеряно"))
            self.root.after(0, self.disconnect)
            
    def display_message(self, data):
        """Отображение сообщения в интерфейсе"""
        self.root.after(0, lambda: self._display_message_threadsafe(data))
        
    def _display_message_threadsafe(self, data):
        """Потокобезопасное отображение сообщения"""
        msg_type = data.get('type', '')
        
        if msg_type == 'message':
            is_my_message = data.get('username') == self.username
            self.create_message_widget(data, is_my_message)
            
        elif msg_type == 'delete_message':
            message_id = data.get('message_id')
            self.remove_message_widget(message_id)
            
        elif msg_type in ['system', 'notification', 'error', 'users_list', 'chat_changed']:
            # Создаем системное сообщение
            system_data = {
                'id': f"sys_{time.time()}",
                'username': 'System',
                'avatar': '⚡',
                'message': data.get('message', ''),
                'timestamp': data.get('timestamp', time.time()),
                'can_delete': False
            }
            self.create_message_widget(system_data, False)
            
    def on_closing(self):
        """Обработка закрытия окна"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.root.destroy()

if __name__ == "__main__":
    client = TelegramClient()
    client.root.mainloop()