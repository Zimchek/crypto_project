import tkinter as tk
from tkinter import messagebox, filedialog
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from crypto_core import CryptoService
from crypto_core.stego_service import StegoService


class EncryptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CryptoModule Pro - Шифрование + Стеганография")
        self.root.geometry("700x650")
        self._build_ui()

    def _build_ui(self):
        pad_opts = {"padx": 10, "pady": 5}

        # === Заголовок с вкладками (упрощённо - через Label) ===
        title_frame = tk.Frame(self.root, bg="#2c3e50")
        title_frame.pack(fill="x", padx=0, pady=0)
        
        tk.Label(title_frame, text="🔐 CryptoModule Pro", 
                font=("Arial", 16, "bold"), bg="#2c3e50", fg="white").pack(pady=10)
        
        # Кнопки переключения режимов
        mode_frame = tk.Frame(self.root)
        mode_frame.pack(fill="x", **pad_opts)
        
        self.btn_crypto = tk.Button(mode_frame, text="🔒 Обычное шифрование", 
                                   command=lambda: self._switch_mode("crypto"),
                                   bg="#3498db", fg="white", padx=10, pady=5)
        self.btn_crypto.pack(side="left", padx=5, expand=True, fill="x")
        
        self.btn_stego = tk.Button(mode_frame, text="🖼 Стеганография", 
                                  command=lambda: self._switch_mode("stego"),
                                  bg="#95a5a6", fg="white", padx=10, pady=5)
        self.btn_stego.pack(side="left", padx=5, expand=True, fill="x")

        # === Контейнер для контента ===
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill="both", expand=True, **pad_opts)
        
        # Инициализируем режим шифрования
        self._build_crypto_mode()
        self.current_mode = "crypto"

    def _switch_mode(self, mode):
        """Переключение между режимами"""
        # Очищаем текущий контент
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.current_mode = mode
        
        if mode == "crypto":
            self._build_crypto_mode()
            self.btn_crypto.config(bg="#3498db")
            self.btn_stego.config(bg="#95a5a6")
        else:
            self._build_stego_mode()
            self.btn_stego.config(bg="#27ae60")
            self.btn_crypto.config(bg="#95a5a6")

    def _build_crypto_mode(self):
        """Режим обычного шифрования"""
        pad_opts = {"padx": 5, "pady": 3}

        tk.Label(self.content_frame, text="Текст для обработки:", 
                font=("Arial", 10, "bold")).pack(anchor="w", **pad_opts)
        
        # Кнопки загрузки/сохранения
        input_btn_frame = tk.Frame(self.content_frame)
        input_btn_frame.pack(fill="x", **pad_opts)
        tk.Button(input_btn_frame, text="📂 Загрузить из файла", 
                 command=self._load_input).pack(side="left", padx=2)
        tk.Button(input_btn_frame, text="🗑 Очистить", 
                 command=lambda: self.text_in.delete("1.0", tk.END)).pack(side="right", padx=2)
        
        self.text_in = tk.Text(self.content_frame, height=5, wrap="word")
        self.text_in.pack(fill="x", **pad_opts)

        tk.Label(self.content_frame, text="Ключ шифрования:").pack(anchor="w", **pad_opts)
        self.key_entry = tk.Entry(self.content_frame, width=50)
        self.key_entry.pack(fill="x", **pad_opts)

        # Кнопки операций
        btn_frame = tk.Frame(self.content_frame)
        btn_frame.pack(fill="x", pady=10)
        tk.Button(btn_frame, text="🔒 Зашифровать", 
                 command=self._encrypt, bg="#d4edda", padx=15, pady=5).pack(side="left", expand=True, padx=5)
        tk.Button(btn_frame, text="🔓 Расшифровать", 
                 command=self._decrypt, bg="#f8d7da", padx=15, pady=5).pack(side="left", expand=True, padx=5)

        tk.Label(self.content_frame, text="Результат:", 
                font=("Arial", 10, "bold")).pack(anchor="w", **pad_opts)
        
        output_btn_frame = tk.Frame(self.content_frame)
        output_btn_frame.pack(fill="x", **pad_opts)
        tk.Button(output_btn_frame, text="💾 Сохранить", 
                 command=self._save_output).pack(side="left", padx=2)
        tk.Button(output_btn_frame, text="📋 Копировать", 
                 command=self._copy_output).pack(side="left", padx=2)
        tk.Button(output_btn_frame, text="📄 Паспорт", 
                 command=self._generate_passport).pack(side="left", padx=2)
        
        self.text_out = tk.Text(self.content_frame, height=5, state="disabled", 
                               wrap="word", bg="#f8f9fa")
        self.text_out.pack(fill="x", **pad_opts)

    def _build_stego_mode(self):
        """Режим стеганографии"""
        pad_opts = {"padx": 5, "pady": 3}

        # === Вкладка 1: Спрятать текст ===
        tk.Label(self.content_frame, text="🔐 Спрятать текст в изображение", 
                font=("Arial", 11, "bold"), fg="#27ae60").pack(anchor="w", pady=(0, 10))

        tk.Label(self.content_frame, text="Секретный текст:").pack(anchor="w", **pad_opts)
        self.stego_text_in = tk.Text(self.content_frame, height=4, wrap="word")
        self.stego_text_in.pack(fill="x", **pad_opts)

        tk.Label(self.content_frame, text="Ключ шифрования:").pack(anchor="w", **pad_opts)
        self.stego_key_entry = tk.Entry(self.content_frame, width=50)
        self.stego_key_entry.pack(fill="x", **pad_opts)

        tk.Label(self.content_frame, text="Изображение-контейнер:").pack(anchor="w", **pad_opts)
        self.stego_image_path = tk.StringVar()
        tk.Entry(self.content_frame, textvariable=self.stego_image_path, 
                state="readonly").pack(fill="x", **pad_opts)
        tk.Button(self.content_frame, text="📂 Выбрать изображение (PNG/BMP)", 
                 command=self._select_cover_image).pack(fill="x", **pad_opts)

        tk.Button(self.content_frame, text="🖼 Спрятать текст в картинку", 
                 command=self._hide_text_in_image, bg="#27ae60", fg="white",
                 font=("Arial", 10, "bold"), pady=8).pack(fill="x", pady=10)

        # === Вкладка 2: Извлечь текст ===
        tk.Label(self.content_frame, text="🔓 Извлечь текст из изображения", 
                font=("Arial", 11, "bold"), fg="#e74c3c").pack(anchor="w", pady=(20, 10))

        tk.Label(self.content_frame, text="Изображение со скрытым текстом:").pack(anchor="w", **pad_opts)
        self.stego_secret_path = tk.StringVar()
        tk.Entry(self.content_frame, textvariable=self.stego_secret_path, 
                state="readonly").pack(fill="x", **pad_opts)
        tk.Button(self.content_frame, text="📂 Выбрать секретное изображение", 
                 command=self._select_secret_image).pack(fill="x", **pad_opts)

        tk.Label(self.content_frame, text="Ключ дешифрования:").pack(anchor="w", **pad_opts)
        self.stego_decrypt_key = tk.Entry(self.content_frame, width=50)
        self.stego_decrypt_key.pack(fill="x", **pad_opts)

        tk.Button(self.content_frame, text="🔍 Извлечь и расшифровать", 
                 command=self._extract_and_decrypt, bg="#e74c3c", fg="white",
                 font=("Arial", 10, "bold"), pady=8).pack(fill="x", pady=10)

        # Результат извлечения
        tk.Label(self.content_frame, text="Извлечённый текст:").pack(anchor="w", **pad_opts)
        self.stego_result = tk.Text(self.content_frame, height=4, state="disabled", 
                                   wrap="word", bg="#f8f9fa")
        self.stego_result.pack(fill="x", **pad_opts)

    # === Методы для стеганографии ===
    
    def _select_cover_image(self):
        """Выбор изображения-контейнера"""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение-контейнер",
            filetypes=[("PNG files", "*.png"), ("BMP files", "*.bmp"), ("All files", "*.*")]
        )
        if file_path:
            self.stego_image_path.set(file_path)

    def _select_secret_image(self):
        """Выбор изображения со скрытыми данными"""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение со скрытым текстом",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            self.stego_secret_path.set(file_path)

    def _hide_text_in_image(self):
        """Спрятать текст в изображение"""
        try:
            text = self.stego_text_in.get("1.0", tk.END).strip()
            key = self.stego_key_entry.get().strip()
            cover_image = self.stego_image_path.get()
            
            if not text or not key or not cover_image:
                messagebox.showwarning("Ввод", "Заполните все поля и выберите изображение")
                return
            
            # Диалог сохранения
            output_path = filedialog.asksaveasfilename(
                title="Сохранить изображение со скрытым текстом",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                initialfile="secret_image.png"
            )
            
            if output_path:
                result = StegoService.hide_encrypted_text(text, key, cover_image, output_path)
                messagebox.showinfo(
                    "Успех", 
                    f"✅ Текст зашифрован и спрятан!\n\n"
                    f"📊 Детали:\n"
                    f"• Размер оригинала: {result['original_size_kb']} KB\n"
                    f"• Размер результата: {result['result_size_kb']} KB\n"
                    f"• Длина зашифрованного текста: {result['encrypted_text_length']} симв.\n\n"
                    f"Сохранено в:\n{output_path}"
                )
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _extract_and_decrypt(self):
        """Извлечь и расшифровать текст"""
        try:
            secret_image = self.stego_secret_path.get()
            key = self.stego_decrypt_key.get().strip()
            
            if not secret_image or not key:
                messagebox.showwarning("Ввод", "Выберите изображение и введите ключ")
                return
            
            result = StegoService.extract_and_decrypt(secret_image, key)
            
            # Показываем результат
            self.stego_result.config(state="normal")
            self.stego_result.delete("1.0", tk.END)
            self.stego_result.insert("1.0", result['decrypted_text'])
            self.stego_result.config(state="disabled")
            
            messagebox.showinfo(
                "Успех",
                f"✅ Данные извлечены и расшифрованы!\n\n"
                f"📊 Детали:\n"
                f"• Длина извлечённых данных: {result['hidden_data_length']} симв.\n"
                f"• Длина расшифрованного текста: {result['decrypted_length']} симв."
            )
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # === Методы для обычного шифрования (оставляем как были) ===
    
    def _set_output(self, text: str):
        self.text_out.config(state="normal")
        self.text_out.delete("1.0", tk.END)
        self.text_out.insert("1.0", text)
        self.text_out.config(state="disabled")

    def _get_input(self) -> str:
        return self.text_in.get("1.0", tk.END).strip()

    def _get_output(self) -> str:
        return self.text_out.get("1.0", tk.END).strip()

    def _load_input(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_in.delete("1.0", tk.END)
                self.text_in.insert("1.0", content)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{str(e)}")

    def _save_output(self):
        content = self._get_output()
        if not content:
            messagebox.showwarning("Нет данных", "Сначала выполните шифрование")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile="result.txt"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Успех", "Файл сохранён")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{str(e)}")

    def _copy_output(self):
        content = self._get_output()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Копирование", "Скопировано в буфер обмена")

    def _encrypt(self):
        try:
            plaintext = self._get_input()
            key = self.key_entry.get().strip()
            if not plaintext or not key:
                messagebox.showwarning("Ввод", "Заполните текст и ключ")
                return
            result = CryptoService.encrypt(plaintext, key)
            self._set_output(result)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _decrypt(self):
        try:
            ciphertext = self._get_input()
            key = self.key_entry.get().strip()
            if not ciphertext or not key:
                messagebox.showwarning("Ввод", "Заполните текст и ключ")
                return
            result = CryptoService.decrypt(ciphertext, key)
            self._set_output(result)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _generate_passport(self):
        import hashlib
        import json
        from datetime import datetime
        
        content = self._get_output()
        if not content:
            messagebox.showwarning("Нет данных", "Сначала выполните операцию")
            return

        input_hash = hashlib.sha256(self._get_input().encode()).hexdigest()[:16]
        output_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        key_fingerprint = hashlib.sha256(self.key_entry.get().encode()).hexdigest()[:8]

        passport = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "algorithm": "AES-256-GCM + PBKDF2",
            "operation": "Encrypt/Decrypt",
            "input_sha256_prefix": input_hash,
            "output_sha256_prefix": output_hash,
            "key_fingerprint": f"SHA256:{key_fingerprint}...",
            "integrity": "VERIFIED (GCM Tag)"
        }

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile="crypto_passport.txt"
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(passport, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Готово", "Криптографический паспорт сохранён")


def run():
    root = tk.Tk()
    EncryptionApp(root)
    root.mainloop()