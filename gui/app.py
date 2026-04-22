import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import shutil
import json
import hashlib
from datetime import datetime

# 1. Импорт Drag-and-Drop
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    TKDND_AVAILABLE = True
except ImportError:
    TKDND_AVAILABLE = False
    print("⚠️ tkinterdnd2 не найден. Drag-and-drop отключен.")

# 2. Импорт базы данных
try:
    from crypto_core.db_manager import AuditDB
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("⚠️ db_manager не найден. Логирование в БД отключено.")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from crypto_core import CryptoService
    from crypto_core.stego_service import StegoService
except ImportError as e:
    print(f"Ошибка импорта модулей: {e}")
    sys.exit(1)


class ActivityLogger:
    """Класс для логирования действий пользователя в файл"""
    
    def __init__(self, log_dir):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = None
        self.session_date = datetime.now().strftime("%Y-%m-%d")
        self._init_log_file()
    
    def _init_log_file(self):
        """Создает новый файл лога с заголовком"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"activity_log_{timestamp}.txt"
        self.log_path = os.path.join(self.log_dir, log_filename)
        
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write(" " * 20 + "CRYPTO PROJECT - ACTIVITY LOG\n")
            f.write(" " * 25 + f"Date: {self.session_date}\n")
            f.write("=" * 80 + "\n")
            f.write("\n")
            f.write(f"Session started at: {datetime.now().strftime('%H:%M:%S')}\n")
            f.write("-" * 80 + "\n\n")
    
    def log(self, action: str):
        """Записывает действие в лог с временной меткой"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {action}\n")
        except:
            pass
    
    def log_section(self, section_name: str):
        """Добавляет разделитель секции"""
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write("\n" + "-" * 80 + "\n")
                f.write(f">>> {section_name}\n")
                f.write("-" * 80 + "\n")
        except:
            pass


class EncryptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CryptoProject Pro")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        self.root.configure(bg="white")

        style = ttk.Style()
        style.theme_use('clam')

        # Настройка путей
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        self.CACHE_DIR = os.path.join(base_dir, "cache")
        os.makedirs(self.CACHE_DIR, exist_ok=True)
        
        # Папка для логов
        self.LOG_DIR = os.path.join(self.CACHE_DIR, "logs")
        os.makedirs(self.LOG_DIR, exist_ok=True)
        
        # Инициализация логгера
        self.logger = ActivityLogger(self.LOG_DIR)
        self.logger.log("APPLICATION STARTED")
        self.logger.log(f"Cache directory: {self.CACHE_DIR}")

        # Инициализация базы данных
                # Инициализация базы данных
        self.db = None
        if DB_AVAILABLE:
            try:
                self.db = AuditDB()  # ← ← ← ИЗМЕНИ ТОЛЬКО ЭТУ СТРОКУ
                self.logger.log("DATABASE CONNECTED: SQLite (audit.db)")
            except Exception as e:
                self.logger.log(f"DATABASE CONNECTION FAILED: {str(e)}")
                print(f"⚠️ База данных не подключена: {e}")
                print("Приложение будет работать без логирования в БД")

        self.stego_cover_path = tk.StringVar()
        self.stego_secret_path = tk.StringVar()

        self._build_main_interface()
        
        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_main_interface(self):
        """Создает интерфейс с прокруткой"""
        
        # === ВЕРХНЯЯ ПАНЕЛЬ ===
        header = tk.Frame(self.root, bg="white", height=60)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        tk.Label(header, text="🛡️ CryptoProject Pro", 
                 font=("Segoe UI", 18, "bold"), bg="white", fg="#2c3e50").pack(pady=15)

        mode_frame = tk.Frame(self.root, bg="white")
        mode_frame.pack(fill="x", pady=5)

        self.btn_mode_crypto = ttk.Button(mode_frame, text="🔒 Шифрование текста", 
                                          command=lambda: self._switch_mode("crypto"), width=25)
        self.btn_mode_crypto.pack(side="left", padx=10, pady=5)

        self.btn_mode_stego = ttk.Button(mode_frame, text="🖼 Стеганография", 
                                         command=lambda: self._switch_mode("stego"), width=25)
        self.btn_mode_stego.pack(side="left", padx=10, pady=5)

        self.btn_clear_cache = ttk.Button(mode_frame, text="🗑 Очистить кеш", 
                                          command=self._clear_cache)
        self.btn_clear_cache.pack(side="right", padx=10, pady=5)

        # === ЗОНА ПРОКРУТКИ (CANVAS + SCROLLBAR) ===
        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True, padx=15, pady=10)

        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.content_frame = tk.Frame(self.canvas, bg="white")
        self.window_id = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        # Логика прокрутки и растягивания ширины
        def _on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        def _on_canvas_configure(event):
            self.canvas.itemconfig(self.window_id, width=event.width)
        
        self.content_frame.bind("<Configure>", _on_frame_configure)
        self.canvas.bind("<Configure>", _on_canvas_configure)

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self._switch_mode("crypto")

    def _switch_mode(self, mode):
        self.logger.log(f"SWITCHED MODE: {mode.upper()}")
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if mode == "crypto":
            self._build_crypto_view()
        else:
            self._build_stego_view()

    # ==========================================
    # 🔹 РЕЖИМ 1: ШИФРОВАНИЕ
    # ==========================================

    def _build_crypto_view(self):
        tk.Label(self.content_frame, text="Введите текст для обработки:", 
                 font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w", pady=(10, 5))

        self.txt_input = tk.Text(self.content_frame, height=8, font=("Consolas", 10))
        self.txt_input.pack(fill="x", pady=5)

        input_toolbar = tk.Frame(self.content_frame, bg="white")
        input_toolbar.pack(fill="x")
        tk.Button(input_toolbar, text="📂 Загрузить файл", 
                  command=lambda: self._load_file()).pack(side="left", padx=5)
        tk.Button(input_toolbar, text="❌ Очистить", 
                  command=lambda: self._clear_input_field()).pack(side="left", padx=5)

        tk.Label(self.content_frame, text="Секретный ключ:", font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w", pady=(10, 5))
        self.entry_key = tk.Entry(self.content_frame, font=("Segoe UI", 11))
        self.entry_key.pack(fill="x", pady=5)

        actions_frame = tk.Frame(self.content_frame, bg="white")
        actions_frame.pack(fill="x", pady=15)
        
        tk.Button(actions_frame, text="🔒 Зашифровать", 
                  command=lambda: self._action_encrypt(), 
                  bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold")).pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(actions_frame, text="🔓 Расшифровать", 
                  command=lambda: self._action_decrypt(), 
                  bg="#e74c3c", fg="white", font=("Segoe UI", 11, "bold")).pack(side="left", fill="x", expand=True, padx=5)

        tk.Label(self.content_frame, text="Результат:", font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w", pady=(5, 5))
        
        self.txt_output = tk.Text(self.content_frame, height=8, font=("Consolas", 10), bg="#f0f0f0", state="disabled")
        self.txt_output.pack(fill="x", pady=5)

        output_toolbar = tk.Frame(self.content_frame, bg="white")
        output_toolbar.pack(fill="x", pady=10)
        tk.Button(output_toolbar, text="💾 Сохранить", 
                  command=lambda: self._save_result()).pack(side="left", padx=5)
        tk.Button(output_toolbar, text="📄 Паспорт", 
                  command=lambda: self._create_passport()).pack(side="left", padx=5)
        tk.Button(output_toolbar, text="📋 Копировать", 
                  command=lambda: self._copy_result()).pack(side="right", padx=5)

        tk.Label(self.content_frame, text="", height=5, bg="white").pack()

    # ==========================================
    # 🔹 РЕЖИМ 2: СТЕГАНОГРАФИЯ
    # ==========================================

    def _build_stego_view(self):
        tk.Label(self.content_frame, text="🔐 Спрятать текст в изображение", 
                 font=("Segoe UI", 12, "bold"), bg="white", fg="#27ae60").pack(anchor="w", pady=(10, 5))
        
        tk.Label(self.content_frame, text="Сообщение:", bg="white").pack(anchor="w", pady=(5,0))
        self.stego_txt_input = tk.Text(self.content_frame, height=3)
        self.stego_txt_input.pack(fill="x", pady=5)

        tk.Label(self.content_frame, text="Ключ шифрования:", bg="white").pack(anchor="w")
        self.stego_entry_key = tk.Entry(self.content_frame)
        self.stego_entry_key.pack(fill="x", pady=5)

        # Drag-and-Drop Зона 1
        tk.Label(self.content_frame, text="Картинка-контейнер (перетащите PNG/BMP):", bg="white").pack(anchor="w", pady=(10, 5))
        
        self.cover_drop_zone = tk.Label(self.content_frame, text="📁 Перетащите сюда или нажмите", 
                                        bg="#ecf0f1", fg="#7f8c8d", font=("Segoe UI", 10), 
                                        relief="ridge", bd=2, padx=20, pady=30, cursor="hand2")
        self.cover_drop_zone.pack(fill="x", pady=5)
        
        if TKDND_AVAILABLE:
            self.cover_drop_zone.drop_target_register(DND_FILES)
            self.cover_drop_zone.dnd_bind('<<Drop>>', lambda e: self._handle_drop(e, self.stego_cover_path, self.cover_drop_zone))
        self.cover_drop_zone.bind("<Button-1>", lambda e: self._select_cover_image())
        
        self.cover_path_label = tk.Label(self.content_frame, text="Файл не выбран", fg="#95a5a6", font=("Segoe UI", 8), bg="white", wraplength=700)
        self.cover_path_label.pack(fill="x")

        tk.Button(self.content_frame, text="✨ Спрятать в картинку", 
                  command=lambda: self._action_hide(), 
                  bg="#27ae60", fg="white", font=("Segoe UI", 11, "bold")).pack(fill="x", pady=15)

        ttk.Separator(self.content_frame, orient="horizontal").pack(fill="x", pady=20)

        # Блок Извлечения
        tk.Label(self.content_frame, text="🔍 Извлечь текст из изображения", 
                 font=("Segoe UI", 12, "bold"), bg="white", fg="#c0392b").pack(anchor="w")

        tk.Label(self.content_frame, text="Картинка с секретом (перетащите PNG):", bg="white").pack(anchor="w", pady=(10, 5))
        
        self.secret_drop_zone = tk.Label(self.content_frame, text="📁 Перетащите сюда или нажмите", 
                                         bg="#ecf0f1", fg="#7f8c8d", font=("Segoe UI", 10), 
                                         relief="ridge", bd=2, padx=20, pady=30, cursor="hand2")
        self.secret_drop_zone.pack(fill="x", pady=5)
        
        if TKDND_AVAILABLE:
            self.secret_drop_zone.drop_target_register(DND_FILES)
            self.secret_drop_zone.dnd_bind('<<Drop>>', lambda e: self._handle_drop(e, self.stego_secret_path, self.secret_drop_zone))
        self.secret_drop_zone.bind("<Button-1>", lambda e: self._select_secret_image())
        
        self.secret_path_label = tk.Label(self.content_frame, text="Файл не выбран", fg="#95a5a6", font=("Segoe UI", 8), bg="white", wraplength=700)
        self.secret_path_label.pack(fill="x")

        tk.Label(self.content_frame, text="Ключ дешифрования:", bg="white").pack(anchor="w", pady=(10, 5))
        self.stego_entry_key_decrypt = tk.Entry(self.content_frame)
        self.stego_entry_key_decrypt.pack(fill="x", pady=5)

        # Кнопки извлечения и ОЧИСТКИ
        actions_frame_stego = tk.Frame(self.content_frame, bg="white")
        actions_frame_stego.pack(fill="x", pady=10)
        
        tk.Button(actions_frame_stego, text="🔍 Извлечь", 
                  command=lambda: self._action_extract(), 
                  bg="#c0392b", fg="white", font=("Segoe UI", 11, "bold")).pack(side="left", fill="x", expand=True, padx=5)
        
        tk.Button(actions_frame_stego, text="🧹 Очистить результат", 
                  command=lambda: self._clear_stego_result(), 
                  bg="#f39c12", fg="white", font=("Segoe UI", 11, "bold")).pack(side="left", fill="x", expand=True, padx=5)

        tk.Label(self.content_frame, text="Результат:", bg="white").pack(anchor="w", pady=(5,0))
        self.stego_txt_output = tk.Text(self.content_frame, height=4, state="disabled", bg="#f9f9f9")
        self.stego_txt_output.pack(fill="x", pady=5)

        tk.Label(self.content_frame, text="", height=5, bg="white").pack()

    def _handle_drop(self, event, path_var, drop_zone):
        file_path = event.data.strip('{}')
        if file_path.lower().endswith(('.png', '.bmp')):
            path_var.set(file_path)
            filename = os.path.basename(file_path)
            drop_zone.config(text=f"✅ {filename}", bg="#d5f5e3", fg="#27ae60")
            if path_var == self.stego_cover_path:
                self.cover_path_label.config(text=file_path, fg="#27ae60")
                self.logger.log(f"DRAG-DROP COVER IMAGE: {filename}")
                if self.db:
                    self.db.log_operation("FILE_SELECT", "STEGO", "SUCCESS", input_file=filename)
            else:
                self.secret_path_label.config(text=file_path, fg="#c0392b")
                self.logger.log(f"DRAG-DROP SECRET IMAGE: {filename}")
        else:
            messagebox.showwarning("Неверный формат", "Перетащите файл PNG или BMP")
            self.logger.log("DRAG-DROP FAILED: Invalid file format")

    # ==========================================
    # ⚙️ ЛОГИКА С ЛОГИРОВАНИЕМ
    # ==========================================

    def _action_encrypt(self):
        self.logger.log("BUTTON CLICKED: ENCRYPT")
        self._process_crypto(self._action_encrypt_logic, self.txt_input, self.entry_key, self.txt_output, "ENCRYPT")

    def _action_decrypt(self):
        self.logger.log("BUTTON CLICKED: DECRYPT")
        self._process_crypto(self._action_decrypt_logic, self.txt_input, self.entry_key, self.txt_output, "DECRYPT")

    def _process_crypto(self, logic_func, input_widget, key_widget, output_widget, op_type):
        try:
            text = input_widget.get("1.0", tk.END).strip()
            key = key_widget.get().strip()
            if not text or not key:
                self.logger.log("ERROR: Empty text or key")
                if self.db:
                    self.db.log_operation(op_type, "AES-256-GCM", "FAILED", error="Empty text or key")
                messagebox.showwarning("Ошибка", "Заполните текст и ключ!")
                return
            result = logic_func(text, key)
            output_widget.config(state="normal")
            output_widget.delete("1.0", tk.END)
            output_widget.insert("1.0", result)
            output_widget.config(state="disabled")
            self.logger.log(f"CRYPTO OPERATION SUCCESS: {op_type} - {len(result)} chars")
            if self.db:
                self.db.log_operation(op_type, "AES-256-GCM", "SUCCESS", key=key)
        except Exception as e:
            self.logger.log(f"CRYPTO OPERATION FAILED: {str(e)}")
            if self.db:
                self.db.log_operation(op_type, "AES-256-GCM", "FAILED", key=key, error=str(e))
            messagebox.showerror("Ошибка", str(e))

    def _action_encrypt_logic(self, text, key): 
        self.logger.log("ALGORITHM: AES-256 ENCRYPT")
        return CryptoService.encrypt(text, key)
    
    def _action_decrypt_logic(self, text, key): 
        self.logger.log("ALGORITHM: AES-256 DECRYPT")
        return CryptoService.decrypt(text, key)

    def _action_hide(self):
        self.logger.log("BUTTON CLICKED: HIDE IN IMAGE (STEGO)")
        try:
            text = self.stego_txt_input.get("1.0", tk.END).strip()
            key = self.stego_entry_key.get().strip()
            cover = self.stego_cover_path.get()
            if not text or not key or not cover:
                self.logger.log("ERROR: Missing fields for stego hide")
                if self.db:
                    self.db.log_operation("STEGO_HIDE", "LSB+AES", "FAILED", error="Missing fields")
                messagebox.showwarning("Ошибка", "Заполните все поля!")
                return
            
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            out_path = os.path.join(self.CACHE_DIR, f"stego_secret_{now}.png")
            
            StegoService.hide_encrypted_text(text, key, cover, out_path)
            self.logger.log(f"STEGO HIDE SUCCESS: {os.path.basename(out_path)}")
            if self.db:
                self.db.log_operation("STEGO_HIDE", "LSB+AES", "SUCCESS", 
                                     input_file=os.path.basename(cover), 
                                     output_file=os.path.basename(out_path),
                                     key=key)
            messagebox.showinfo("Успех", f"Секрет спрятан!\nФайл сохранен в:\n{out_path}")
        except Exception as e:
            self.logger.log(f"STEGO HIDE FAILED: {str(e)}")
            if self.db:
                self.db.log_operation("STEGO_HIDE", "LSB+AES", "FAILED", key=key, error=str(e))
            messagebox.showerror("Ошибка", str(e))

    def _action_extract(self):
        self.logger.log("BUTTON CLICKED: EXTRACT FROM IMAGE (STEGO)")
        try:
            secret = self.stego_secret_path.get()
            key = self.stego_entry_key_decrypt.get().strip()
            if not secret or not key:
                self.logger.log("ERROR: Missing fields for stego extract")
                if self.db:
                    self.db.log_operation("STEGO_EXTRACT", "LSB+AES", "FAILED", error="Missing fields")
                messagebox.showwarning("Ошибка", "Выберите картинку и введите ключ!")
                return
            result = StegoService.extract_and_decrypt(secret, key)
            self.stego_txt_output.config(state="normal")
            self.stego_txt_output.delete("1.0", tk.END)
            self.stego_txt_output.insert("1.0", result['decrypted_text'])
            self.stego_txt_output.config(state="disabled")
            self.logger.log(f"STEGO EXTRACT SUCCESS: {len(result['decrypted_text'])} chars")
            if self.db:
                self.db.log_operation("STEGO_EXTRACT", "LSB+AES", "SUCCESS", 
                                     input_file=os.path.basename(secret),
                                     key=key)
            messagebox.showinfo("Успех", "Текст извлечён!")
        except Exception as e:
            self.logger.log(f"STEGO EXTRACT FAILED: {str(e)}")
            if self.db:
                self.db.log_operation("STEGO_EXTRACT", "LSB+AES", "FAILED", key=key, error=str(e))
            messagebox.showerror("Ошибка", str(e))

    def _clear_stego_result(self):
        self.logger.log("BUTTON CLICKED: CLEAR STEGO RESULT")
        self.stego_txt_output.config(state="normal")
        self.stego_txt_output.delete("1.0", tk.END)
        self.stego_txt_output.config(state="disabled")

    def _load_file(self):
        self.logger.log("BUTTON CLICKED: LOAD FILE")
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.txt_input.delete("1.0", tk.END)
                    self.txt_input.insert("1.0", content)
                self.logger.log(f"FILE LOADED: {os.path.basename(path)} ({len(content)} chars)")
                if self.db:
                    self.db.log_operation("FILE_LOAD", "SYSTEM", "SUCCESS", input_file=os.path.basename(path))
            except Exception as e:
                self.logger.log(f"FILE LOAD FAILED: {str(e)}")
                messagebox.showerror("Ошибка", str(e))

    def _clear_input_field(self):
        self.logger.log("BUTTON CLICKED: CLEAR INPUT FIELD")
        self.txt_input.delete("1.0", tk.END)

    def _save_result(self):
        self.logger.log("BUTTON CLICKED: SAVE RESULT")
        text = self.txt_output.get("1.0", tk.END).strip()
        if not text: 
            self.logger.log("SAVE FAILED: No content")
            return
        
        now = datetime.now().strftime("%Y-%m-%d_%H-%M")
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", 
            initialdir=self.CACHE_DIR,
            initialfile=f"encrypted_{now}.txt"
        )
        
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f: f.write(text)
                self.logger.log(f"FILE SAVED: {os.path.basename(path)} ({len(text)} chars)")
                if self.db:
                    self.db.log_operation("FILE_SAVE", "SYSTEM", "SUCCESS", output_file=os.path.basename(path))
                messagebox.showinfo("Готово", "Файл сохранён.")
            except Exception as e: 
                self.logger.log(f"FILE SAVE FAILED: {str(e)}")
                messagebox.showerror("Ошибка", str(e))

    def _copy_result(self):
        self.logger.log("BUTTON CLICKED: COPY TO CLIPBOARD")
        text = self.txt_output.get("1.0", tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.logger.log("CLIPBOARD COPY SUCCESS")
            messagebox.showinfo("Копирование", "Скопировано!")

    def _clear_cache(self):
        self.logger.log("BUTTON CLICKED: CLEAR CACHE")
        
        if messagebox.askyesno("Подтверждение", "Удалить временные файлы и результаты работы?\n(История действий будет сохранена)"):
            
            def safe_delete(widget):
                try:
                    if widget and widget.winfo_exists():
                        widget.config(state="normal")
                        widget.delete("1.0", tk.END)
                        widget.config(state="disabled")
                except:
                    pass
            
            def safe_clear_entry(widget):
                try:
                    if widget and widget.winfo_exists():
                        widget.delete(0, tk.END)
                except:
                    pass

            if hasattr(self, 'txt_input'):
                try:
                    if self.txt_input.winfo_exists(): self.txt_input.delete("1.0", tk.END)
                except: pass
                    
            if hasattr(self, 'entry_key'): safe_clear_entry(self.entry_key)
            if hasattr(self, 'txt_output'): safe_delete(self.txt_output)
            if hasattr(self, 'stego_txt_input'):
                try:
                    if self.stego_txt_input.winfo_exists(): self.stego_txt_input.delete("1.0", tk.END)
                except: pass
            if hasattr(self, 'stego_entry_key'): safe_clear_entry(self.stego_entry_key)
            if hasattr(self, 'stego_entry_key_decrypt'): safe_clear_entry(self.stego_entry_key_decrypt)
            if hasattr(self, 'stego_txt_output'): safe_delete(self.stego_txt_output)

            if hasattr(self, 'cover_drop_zone'):
                try:
                    if self.cover_drop_zone.winfo_exists():
                        self.cover_drop_zone.config(text="📁 Перетащите сюда или нажмите", bg="#ecf0f1", fg="#7f8c8d")
                        self.cover_path_label.config(text="Файл не выбран", fg="#95a5a6")
                except: pass
                self.stego_cover_path.set("")
                
            if hasattr(self, 'secret_drop_zone'):
                try:
                    if self.secret_drop_zone.winfo_exists():
                        self.secret_drop_zone.config(text="📁 Перетащите сюда или нажмите", bg="#ecf0f1", fg="#7f8c8d")
                        self.secret_path_label.config(text="Файл не выбран", fg="#95a5a6")
                except: pass
                self.stego_secret_path.set("")

            count = 0
            try:
                for item_name in os.listdir(self.CACHE_DIR):
                    item_path = os.path.join(self.CACHE_DIR, item_name)
                    
                    if item_name == "logs" and os.path.isdir(item_path):
                        continue 

                    if os.path.isfile(item_path): 
                        os.unlink(item_path)
                        count += 1
                    elif os.path.isdir(item_path): 
                        shutil.rmtree(item_path)
                        count += 1
                        
            except Exception as e:
                self.logger.log(f"CACHE CLEAR ERROR: {str(e)}")
                print(f"Ошибка при удалении файлов: {e}")
            
            self.logger.log(f"CACHE CLEARED: {count} files deleted (Logs preserved)")
            if self.db:
                self.db.log_operation("CACHE_CLEAR", "SYSTEM", "SUCCESS", error=f"{count} files deleted")
            messagebox.showinfo("Очистка", f"Удалено файлов: {count}\nИстория действий сохранена.")

    def _create_passport(self):
        self.logger.log("BUTTON CLICKED: CREATE PASSPORT")
        text = self.txt_output.get("1.0", tk.END).strip()
        if not text:
            self.logger.log("PASSPORT FAILED: No data")
            messagebox.showwarning("Нет данных", "Сначала выполните шифрование.")
            return
        try:
            data = {
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "algorithm": "AES-256-GCM (StdLib)",
                "integrity": "HMAC-SHA256",
                "output_hash": hashlib.sha256(text.encode()).hexdigest()[:12]
            }
            now = datetime.now().strftime("%Y-%m-%d_%H-%M")
            path = os.path.join(self.CACHE_DIR, f"passport_{now}.json")
            with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)
            self.logger.log(f"PASSPORT CREATED: {os.path.basename(path)}")
            if self.db:
                self.db.log_operation("PASSPORT_CREATE", "SYSTEM", "SUCCESS", output_file=os.path.basename(path))
            messagebox.showinfo("Готово", f"Паспорт сохранен:\n{path}")
        except Exception as e: 
            self.logger.log(f"PASSPORT FAILED: {str(e)}")
            messagebox.showerror("Ошибка", str(e))

    def _select_cover_image(self):
        self.logger.log("BUTTON CLICKED: SELECT COVER IMAGE")
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.bmp")])
        if path:
            self.stego_cover_path.set(path)
            self.cover_drop_zone.config(text=f"✅ {os.path.basename(path)}", bg="#d5f5e3", fg="#27ae60")
            self.cover_path_label.config(text=path, fg="#27ae60")
            self.logger.log(f"COVER IMAGE SELECTED: {os.path.basename(path)}")

    def _select_secret_image(self):
        self.logger.log("BUTTON CLICKED: SELECT SECRET IMAGE")
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.bmp")])
        if path:
            self.stego_secret_path.set(path)
            self.secret_drop_zone.config(text=f"✅ {os.path.basename(path)}", bg="#fadbd8", fg="#c0392b")
            self.secret_path_label.config(text=path, fg="#c0392b")
            self.logger.log(f"SECRET IMAGE SELECTED: {os.path.basename(path)}")

    def _on_close(self):
        """Обработчик закрытия приложения"""
        self.logger.log("APPLICATION CLOSED")
        
        if self.db:
            # Показываем статистику
            try:
                stats = self.db.get_statistics()
                if stats:
                    print(f"\n📊 Статистика сеанса:")
                    print(f"   Всего операций: {stats['total']}")
                    print(f"   Успешных: {stats['success']}")
                    print(f"   Ошибок: {stats['failed']}")
            except:
                pass
            
            self.db.close()
        
        self.root.destroy()


def run():
    if TKDND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    
    app = EncryptionApp(root)
    root.mainloop()

if __name__ == "__main__":
    run()