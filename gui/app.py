import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import shutil
import json
import hashlib
from datetime import datetime

# === Настройка путей ===
# Добавляем корень проекта в пути, чтобы импортировать модули
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Импорт наших модулей
try:
    from crypto_core import CryptoService
    from crypto_core.stego_service import StegoService
except ImportError as e:
    print(f"Ошибка импорта модулей: {e}")
    sys.exit(1)


class EncryptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CryptoProject Pro")
        self.root.geometry("800x650")
        self.root.minsize(700, 500)
        
        # Настройка стиля (чуть более современный вид)
        style = ttk.Style()
        style.theme_use('clam')

        # Папка для кеша и временных файлов
                # Логика для поиска правильной директории (в коде или в .exe)
        if getattr(sys, 'frozen', False):
            # Если запущено как .exe
            base_dir = os.path.dirname(sys.executable)
        else:
            # Если запущено как скрипт в VS Code
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        self.CACHE_DIR = os.path.join(base_dir, "cache")
        os.makedirs(self.CACHE_DIR, exist_ok=True)

        # Переменные для хранения путей в стеганографии
        self.stego_cover_path = tk.StringVar()
        self.stego_secret_path = tk.StringVar()

        self._build_main_interface()

    def _build_main_interface(self):
        """Создает верхнюю панель и переключатели режимов"""
        
        # Верхняя панель (Header)
        header = tk.Frame(self.root, bg="#2c3e50", height=60)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        tk.Label(header, text="🛡️ CryptoProject Pro", 
                 font=("Segoe UI", 18, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(pady=15)

        # Панель переключения режимов
        mode_frame = tk.Frame(self.root, bg="#ecf0f1")
        mode_frame.pack(fill="x", pady=5)

        self.btn_mode_crypto = ttk.Button(mode_frame, text="🔒 Шифрование текста", 
                                          command=lambda: self._switch_mode("crypto"), width=25)
        self.btn_mode_crypto.pack(side="left", padx=10, pady=5)

        self.btn_mode_stego = ttk.Button(mode_frame, text="️Стеганография", 
                                         command=lambda: self._switch_mode("stego"), width=25)
        self.btn_mode_stego.pack(side="left", padx=10, pady=5)

        # Кнопка очистки кеша
        self.btn_clear_cache = ttk.Button(mode_frame, text=" Очистить кеш", 
                                          command=self._clear_cache, style="Danger.TButton")
        self.btn_clear_cache.pack(side="right", padx=10, pady=5)

        # Основной контейнер контента
        self.content_frame = tk.Frame(self.root, bg="#ffffff")
        self.content_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # По умолчанию открываем режим шифрования
        self._switch_mode("crypto")

    def _switch_mode(self, mode):
        """Переключает режимы отображения"""
        # Очистка текущего контента
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if mode == "crypto":
            self._build_crypto_view()
            self.btn_mode_crypto.state(["active"])
            self.btn_mode_stego.state(["!active"])
        else:
            self._build_stego_view()
            self.btn_mode_stego.state(["active"])
            self.btn_mode_crypto.state(["!active"])

    # ==========================================
    # 🔹 РЕЖИМ 1: ОБЫЧНОЕ ШИФРОВАНИЕ
    # ==========================================

    def _build_crypto_view(self):
        tk.Label(self.content_frame, text="Введите текст для обработки:", 
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))

        self.txt_input = tk.Text(self.content_frame, height=6, font=("Consolas", 10))
        self.txt_input.pack(fill="x", pady=5)

        # Панель инструментов ввода
        input_toolbar = tk.Frame(self.content_frame)
        input_toolbar.pack(fill="x")
        tk.Button(input_toolbar, text="📂 Загрузить файл", command=self._load_file).pack(side="left", padx=5)
        tk.Button(input_toolbar, text="❌ Очистить поле", command=lambda: self.txt_input.delete("1.0", tk.END)).pack(side="left", padx=5)

        tk.Label(self.content_frame, text="Секретный ключ:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 5))
        self.entry_key = tk.Entry(self.content_frame, font=("Segoe UI", 11))
        self.entry_key.pack(fill="x", pady=5)

        # Кнопки действий
        actions_frame = tk.Frame(self.content_frame)
        actions_frame.pack(fill="x", pady=10)
        
        tk.Button(actions_frame, text="🔒 Зашифровать", command=self._action_encrypt, 
                  bg="#2ecc71", fg="white", font=("Segoe UI", 10, "bold")).pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(actions_frame, text="🔓 Расшифровать", command=self._action_decrypt, 
                  bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold")).pack(side="left", fill="x", expand=True, padx=5)

        tk.Label(self.content_frame, text="Результат:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 5))
        
        self.txt_output = tk.Text(self.content_frame, height=6, font=("Consolas", 10), bg="#f0f0f0", state="disabled")
        self.txt_output.pack(fill="x", pady=5)

        output_toolbar = tk.Frame(self.content_frame)
        output_toolbar.pack(fill="x")
        tk.Button(output_toolbar, text=" Сохранить в файл", command=self._save_result).pack(side="left", padx=5)
        tk.Button(output_toolbar, text="📄 Создать паспорт", command=self._create_passport).pack(side="left", padx=5)
        tk.Button(output_toolbar, text="📋 Копировать", command=self._copy_result).pack(side="right", padx=5)

    # ==========================================
    # 🔹 РЕЖИМ 2: СТЕГАНОГРАФИЯ
    # ==========================================

    def _build_stego_view(self):
        # Блок "Спрятать"
        tk.Label(self.content_frame, text=" Спрятать текст в изображение", 
                 font=("Segoe UI", 12, "bold"), fg="#27ae60").pack(anchor="w")
        
        tk.Label(self.content_frame, text="Сообщение:").pack(anchor="w", pady=(5,0))
        self.stego_txt_input = tk.Text(self.content_frame, height=3)
        self.stego_txt_input.pack(fill="x", pady=5)

        tk.Label(self.content_frame, text="Ключ:").pack(anchor="w")
        self.stego_entry_key = tk.Entry(self.content_frame)
        self.stego_entry_key.pack(fill="x", pady=5)

        tk.Label(self.content_frame, text="Картинка-контейнер:").pack(anchor="w")
        ttk.Entry(self.content_frame, textvariable=self.stego_cover_path, state="readonly").pack(fill="x", pady=2)
        ttk.Button(self.content_frame, text=" Выбрать PNG/BMP", command=self._select_cover_image).pack(fill="x", pady=5)

        tk.Button(self.content_frame, text="✨ Спрятать в картинку", command=self._action_hide, 
                  bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold")).pack(fill="x", pady=10)

        # Разделитель
        ttk.Separator(self.content_frame, orient="horizontal").pack(fill="x", pady=20)

        # Блок "Извлечь"
        tk.Label(self.content_frame, text="🔍 Извлечь текст из изображения", 
                 font=("Segoe UI", 12, "bold"), fg="#c0392b").pack(anchor="w")

        tk.Label(self.content_frame, text="Картинка с секретом:").pack(anchor="w", pady=(5,0))
        ttk.Entry(self.content_frame, textvariable=self.stego_secret_path, state="readonly").pack(fill="x", pady=2)
        ttk.Button(self.content_frame, text="📂 Выбрать картинку", command=self._select_secret_image).pack(fill="x", pady=5)

        tk.Label(self.content_frame, text="Ключ:").pack(anchor="w")
        self.stego_entry_key_decrypt = tk.Entry(self.content_frame)
        self.stego_entry_key_decrypt.pack(fill="x", pady=5)

        tk.Button(self.content_frame, text="🔍 Извлечь", command=self._action_extract, 
                  bg="#c0392b", fg="white", font=("Segoe UI", 10, "bold")).pack(fill="x", pady=10)

        tk.Label(self.content_frame, text="Результат извлечения:").pack(anchor="w", pady=(10,0))
        self.stego_txt_output = tk.Text(self.content_frame, height=4, state="disabled", bg="#f9f9f9")
        self.stego_txt_output.pack(fill="x", pady=5)

    # ==========================================
    # ⚙️ ФУНКЦИОНАЛ (ДЕЙСТВИЯ)
    # ==========================================

    def _action_encrypt(self):
        self._process_crypto(self._action_encrypt_logic, self.txt_input, self.entry_key, self.txt_output)

    def _action_decrypt(self):
        self._process_crypto(self._action_decrypt_logic, self.txt_input, self.entry_key, self.txt_output)

    def _process_crypto(self, logic_func, input_widget, key_widget, output_widget):
        try:
            text = input_widget.get("1.0", tk.END).strip()
            key = key_widget.get().strip()
            
            if not text or not key:
                messagebox.showwarning("Ошибка ввода", "Заполните текст и ключ!")
                return

            result = logic_func(text, key)
            
            output_widget.config(state="normal")
            output_widget.delete("1.0", tk.END)
            output_widget.insert("1.0", result)
            output_widget.config(state="disabled")

        except Exception as e:
            messagebox.showerror("Ошибка обработки", str(e))

    def _action_encrypt_logic(self, text, key):
        return CryptoService.encrypt(text, key)

    def _action_decrypt_logic(self, text, key):
        return CryptoService.decrypt(text, key)

    def _action_hide(self):
        try:
            text = self.stego_txt_input.get("1.0", tk.END).strip()
            key = self.stego_entry_key.get().strip()
            cover = self.stego_cover_path.get()

            if not text or not key or not cover:
                messagebox.showwarning("Ошибка", "Заполните все поля и выберите картинку!")
                return

            # Сохраняем результат сразу в папку cache для порядка
            out_path = os.path.join(self.CACHE_DIR, "stego_result.png")
            
            StegoService.hide_encrypted_text(text, key, cover, out_path)
            messagebox.showinfo("Успех", f"Секрет спрятан!\nФайл сохранен в:\n{out_path}")

        except Exception as e:
            messagebox.showerror("Ошибка стеганографии", str(e))

    def _action_extract(self):
        try:
            secret = self.stego_secret_path.get()
            key = self.stego_entry_key_decrypt.get().strip()

            if not secret or not key:
                messagebox.showwarning("Ошибка", "Выберите картинку и введите ключ!")
                return

            result = StegoService.extract_and_decrypt(secret, key)
            
            self.stego_txt_output.config(state="normal")
            self.stego_txt_output.delete("1.0", tk.END)
            self.stego_txt_output.insert("1.0", result['decrypted_text'])
            self.stego_txt_output.config(state="disabled")
            
            messagebox.showinfo("Успех", "Текст успешно извлечен!")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # ==========================================
    # 🛠 УТИЛИТЫ И ФАЙЛЫ
    # ==========================================

    def _load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.txt_input.delete("1.0", tk.END)
                    self.txt_input.insert("1.0", f.read())
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")

    def _save_result(self):
        text = self.txt_output.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Пусто", "Нет данных для сохранения!")
            return

        path = filedialog.asksaveasfilename(defaultextension=".txt", initialdir=self.CACHE_DIR)
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
                messagebox.showinfo("Готово", "Файл сохранен.")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def _copy_result(self):
        text = self.txt_output.get("1.0", tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Копирование", "Скопировано в буфер обмена.")

    # ==========================================
    # 🗑 ОЧИСТКА КЕША
    # ==========================================

    def _clear_cache(self):
        """Очищает поля ввода и удаляет временные файлы из папки cache"""
        answer = messagebox.askyesno("Подтверждение", 
                                     "Очистить все поля и удалить временные файлы из папки cache?")
        if answer:
            # 1. Очистка полей ввода
            self.txt_input.delete("1.0", tk.END)
            self.txt_output.config(state="normal")
            self.txt_output.delete("1.0", tk.END)
            self.txt_output.config(state="disabled")
            self.entry_key.delete(0, tk.END)

            # Очистка полей стеганографии (если виджеты существуют)
            if hasattr(self, 'stego_txt_input'):
                self.stego_txt_input.delete("1.0", tk.END)
                self.stego_entry_key.delete(0, tk.END)
                self.stego_entry_key_decrypt.delete(0, tk.END)
                self.stego_txt_output.config(state="normal")
                self.stego_txt_output.delete("1.0", tk.END)
                self.stego_txt_output.config(state="disabled")
                self.stego_cover_path.set("")
                self.stego_secret_path.set("")

            # 2. Очистка файлов
            count = 0
            try:
                for filename in os.listdir(self.CACHE_DIR):
                    file_path = os.path.join(self.CACHE_DIR, filename)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                        count += 1
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        count += 1
            except Exception as e:
                messagebox.showerror("Ошибка очистки", f"Не удалось удалить некоторые файлы:\n{e}")

            messagebox.showinfo("Очистка", f"Удалено файлов: {count}\nПоля очищены.")

    # ==========================================
    #  КРИПТОПАСПОРТ
    # ==========================================

    def _create_passport(self):
        text = self.txt_output.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Нет данных", "Сначала выполните шифрование.")
            return

        try:
            # Создаем хеши для отчета
            input_hash = hashlib.sha256(self.txt_input.get("1.0", tk.END).encode()).hexdigest()[:12]
            output_hash = hashlib.sha256(text.encode()).hexdigest()[:12]
            
            passport_data = {
                "app_version": "1.0",
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "algorithm": "AES-256-GCM (StdLib Mode)",
                "integrity_check": "HMAC-SHA256",
                "input_preview_hash": input_hash,
                "output_preview_hash": output_hash,
                "note": "Этот файл не содержит ключей шифрования."
            }

            filename = f"passport_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            save_path = os.path.join(self.CACHE_DIR, filename)

            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(passport_data, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Паспорт", f"Отчет сохранен:\n{save_path}")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # Диалоги выбора файлов для стеганографии
    def _select_cover_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.bmp")])
        if path: self.stego_cover_path.set(path)

    def _select_secret_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.bmp")])
        if path: self.stego_secret_path.set(path)


if __name__ == "__main__":
    root = tk.Tk()
    app = EncryptionApp(root)
    root.mainloop()


def run():
    """Точка входа для запуска приложения"""
    root = tk.Tk()
    app = EncryptionApp(root)
    root.mainloop()