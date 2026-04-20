import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from crypto_core import CryptoService

class EncryptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Модуль шифрования/дешифрования")
        self.root.geometry("600x480")
        self._build_ui()

    def _build_ui(self):
        pad_opts = {"padx": 5, "pady": 5}

        # === Ввод текста ===
        tk.Label(self.root, text="Открытый текст / Шифротекст:").pack(anchor="w", **pad_opts)
        
        # Фрейм для кнопок загрузки/сохранения ввода
        input_btn_frame = tk.Frame(self.root)
        input_btn_frame.pack(fill="x", **pad_opts)
        tk.Button(input_btn_frame, text="📂 Загрузить из файла", command=self._load_input).pack(side="left", padx=2)
        tk.Button(input_btn_frame, text="🗑 Очистить", command=lambda: self.text_in.delete("1.0", tk.END)).pack(side="right", padx=2)
        
        self.text_in = tk.Text(self.root, height=6, wrap="word")
        self.text_in.pack(fill="x", **pad_opts)

        # === Ключ ===
        tk.Label(self.root, text="Ключ:").pack(anchor="w", **pad_opts)
        self.key_entry = tk.Entry(self.root, width=50)
        self.key_entry.pack(fill="x", **pad_opts)

        # === Кнопки шифрования/дешифрования ===
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", **pad_opts)
        tk.Button(btn_frame, text="🔒 Зашифровать", command=self._encrypt, bg="#d4edda").pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(btn_frame, text="🔓 Расшифровать", command=self._decrypt, bg="#f8d7da").pack(side="left", expand=True, fill="x", padx=2)

        # === Результат ===
        tk.Label(self.root, text="Результат:").pack(anchor="w", **pad_opts)
        
        # Фрейм для кнопок результата
        output_btn_frame = tk.Frame(self.root)
        output_btn_frame.pack(fill="x", **pad_opts)
        tk.Button(output_btn_frame, text="💾 Сохранить в файл", command=self._save_output).pack(side="left", padx=2)
        tk.Button(output_btn_frame, text="📋 Копировать", command=self._copy_output).pack(side="right", padx=2)
        
        self.text_out = tk.Text(self.root, height=6, state="disabled", wrap="word", bg="#f8f9fa")
        self.text_out.pack(fill="x", **pad_opts)

    def _set_output(self, text: str):
        self.text_out.config(state="normal")
        self.text_out.delete("1.0", tk.END)
        self.text_out.insert("1.0", text)
        self.text_out.config(state="disabled")

    def _get_input(self) -> str:
        return self.text_in.get("1.0", tk.END).strip()

    # === Методы работы с файлами ===
    
    def _load_input(self):
        """Загрузить текст из файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл для шифрования",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_in.delete("1.0", tk.END)
                self.text_in.insert("1.0", content)
                messagebox.showinfo("Успех", f"Файл загружен: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Ошибка чтения", f"Не удалось прочитать файл:\n{str(e)}")

    def _save_output(self):
        """Сохранить результат в файл"""
        content = self._get_output()
        if not content:
            messagebox.showwarning("Нет данных", "Сначала выполните шифрование или дешифрование")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Сохранить результат",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="encrypted_result.txt"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Успех", f"Результат сохранён в:\n{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Ошибка записи", f"Не удалось сохранить файл:\n{str(e)}")

    def _get_output(self) -> str:
        """Получить текст из output поля"""
        return self.text_out.get("1.0", tk.END).strip()

    def _copy_output(self):
        """Копировать результат в буфер обмена"""
        content = self._get_output()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Копирование", "Результат скопирован в буфер обмена")
        else:
            messagebox.showwarning("Нет данных", "Нечего копировать")

    # === Методы шифрования/дешифрования (без изменений) ===
    
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
                messagebox.showwarning("Ввод", "Заполните шифротекст и ключ")
                return
            result = CryptoService.decrypt(ciphertext, key)
            self._set_output(result)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

def run():
    root = tk.Tk()
    EncryptionApp(root)
    root.mainloop()