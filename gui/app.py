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

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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

        self.stego_cover_path = tk.StringVar()
        self.stego_secret_path = tk.StringVar()

        self._build_main_interface()

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
        tk.Button(input_toolbar, text="📂 Загрузить файл", command=self._load_file).pack(side="left", padx=5)
        tk.Button(input_toolbar, text="❌ Очистить", command=lambda: self.txt_input.delete("1.0", tk.END)).pack(side="left", padx=5)

        tk.Label(self.content_frame, text="Секретный ключ:", font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w", pady=(10, 5))
        self.entry_key = tk.Entry(self.content_frame, font=("Segoe UI", 11))
        self.entry_key.pack(fill="x", pady=5)

        actions_frame = tk.Frame(self.content_frame, bg="white")
        actions_frame.pack(fill="x", pady=15)
        
        tk.Button(actions_frame, text="🔒 Зашифровать", command=self._action_encrypt, 
                  bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold")).pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(actions_frame, text="🔓 Расшифровать", command=self._action_decrypt, 
                  bg="#e74c3c", fg="white", font=("Segoe UI", 11, "bold")).pack(side="left", fill="x", expand=True, padx=5)

        tk.Label(self.content_frame, text="Результат:", font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w", pady=(5, 5))
        
        self.txt_output = tk.Text(self.content_frame, height=8, font=("Consolas", 10), bg="#f0f0f0", state="disabled")
        self.txt_output.pack(fill="x", pady=5)

        output_toolbar = tk.Frame(self.content_frame, bg="white")
        output_toolbar.pack(fill="x", pady=10)
        tk.Button(output_toolbar, text="💾 Сохранить", command=self._save_result).pack(side="left", padx=5)
        tk.Button(output_toolbar, text="📄 Паспорт", command=self._create_passport).pack(side="left", padx=5)
        tk.Button(output_toolbar, text="📋 Копировать", command=self._copy_result).pack(side="right", padx=5)

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

        tk.Button(self.content_frame, text="✨ Спрятать в картинку", command=self._action_hide, 
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
        
        tk.Button(actions_frame_stego, text="🔍 Извлечь", command=self._action_extract, 
                  bg="#c0392b", fg="white", font=("Segoe UI", 11, "bold")).pack(side="left", fill="x", expand=True, padx=5)
        
        # 🔹 КНОПКА ОЧИСТКИ РЕЗУЛЬТАТА
        tk.Button(actions_frame_stego, text="🧹 Очистить результат", command=self._clear_stego_result, 
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
            else:
                self.secret_path_label.config(text=file_path, fg="#c0392b")
        else:
            messagebox.showwarning("Неверный формат", "Перетащите файл PNG или BMP")

    # ==========================================
    # ⚙️ ЛОГИКА
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
                messagebox.showwarning("Ошибка", "Заполните текст и ключ!")
                return
            result = logic_func(text, key)
            output_widget.config(state="normal")
            output_widget.delete("1.0", tk.END)
            output_widget.insert("1.0", result)
            output_widget.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _action_encrypt_logic(self, text, key): return CryptoService.encrypt(text, key)
    def _action_decrypt_logic(self, text, key): return CryptoService.decrypt(text, key)

    def _action_hide(self):
        try:
            text = self.stego_txt_input.get("1.0", tk.END).strip()
            key = self.stego_entry_key.get().strip()
            cover = self.stego_cover_path.get()
            if not text or not key or not cover:
                messagebox.showwarning("Ошибка", "Заполните все поля!")
                return
            
            # 🔹 Имя файла с датой и временем
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            out_path = os.path.join(self.CACHE_DIR, f"stego_secret_{now}.png")
            
            StegoService.hide_encrypted_text(text, key, cover, out_path)
            messagebox.showinfo("Успех", f"Секрет спрятан!\nФайл сохранен в:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

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
            messagebox.showinfo("Успех", "Текст извлечён!")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # 🔹 ФУНКЦИЯ: Очистка результата в стеганографии
    def _clear_stego_result(self):
        self.stego_txt_output.config(state="normal")
        self.stego_txt_output.delete("1.0", tk.END)
        self.stego_txt_output.config(state="disabled")

    def _load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.txt_input.delete("1.0", tk.END)
                    self.txt_input.insert("1.0", f.read())
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def _save_result(self):
        text = self.txt_output.get("1.0", tk.END).strip()
        if not text: return
        
        # 🔹 Имя файла с датой и временем
        now = datetime.now().strftime("%Y-%m-%d_%H-%M")
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", 
            initialdir=self.CACHE_DIR,
            initialfile=f"encrypted_{now}.txt"
        )
        
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f: f.write(text)
                messagebox.showinfo("Готово", "Файл сохранён.")
            except Exception as e: messagebox.showerror("Ошибка", str(e))

    def _copy_result(self):
        text = self.txt_output.get("1.0", tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Копирование", "Скопировано!")

    # 🔹 ИСПРАВЛЕННАЯ ФУНКЦИЯ ОЧИСТКИ КЕША
    def _clear_cache(self):
        if messagebox.askyesno("Подтверждение", "Очистить поля и временные файлы?"):
            # Безопасная очистка текстовых полей с проверкой существования виджетов
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

            # Очистка режима шифрования
            if hasattr(self, 'txt_input'):
                try:
                    if self.txt_input.winfo_exists():
                        self.txt_input.delete("1.0", tk.END)
                except:
                    pass
                    
            if hasattr(self, 'entry_key'):
                safe_clear_entry(self.entry_key)
                
            if hasattr(self, 'txt_output'):
                safe_delete(self.txt_output)

            # Очистка режима стеганографии
            if hasattr(self, 'stego_txt_input'):
                try:
                    if self.stego_txt_input.winfo_exists():
                        self.stego_txt_input.delete("1.0", tk.END)
                except:
                    pass
                    
            if hasattr(self, 'stego_entry_key'):
                safe_clear_entry(self.stego_entry_key)
                
            if hasattr(self, 'stego_entry_key_decrypt'):
                safe_clear_entry(self.stego_entry_key_decrypt)
                
            if hasattr(self, 'stego_txt_output'):
                safe_delete(self.stego_txt_output)

            # Сброс Drag-and-Drop зон
            if hasattr(self, 'cover_drop_zone'):
                try:
                    if self.cover_drop_zone.winfo_exists():
                        self.cover_drop_zone.config(text="📁 Перетащите сюда или нажмите", bg="#ecf0f1", fg="#7f8c8d")
                        self.cover_path_label.config(text="Файл не выбран", fg="#95a5a6")
                except:
                    pass
                self.stego_cover_path.set("")
                
            if hasattr(self, 'secret_drop_zone'):
                try:
                    if self.secret_drop_zone.winfo_exists():
                        self.secret_drop_zone.config(text="📁 Перетащите сюда или нажмите", bg="#ecf0f1", fg="#7f8c8d")
                        self.secret_path_label.config(text="Файл не выбран", fg="#95a5a6")
                except:
                    pass
                self.stego_secret_path.set("")

            # Удаление файлов
            count = 0
            try:
                for f in os.listdir(self.CACHE_DIR):
                    fp = os.path.join(self.CACHE_DIR, f)
                    if os.path.isfile(fp): 
                        os.unlink(fp)
                        count += 1
                    elif os.path.isdir(fp): 
                        shutil.rmtree(fp)
                        count += 1
            except Exception as e:
                print(f"Ошибка при удалении файлов: {e}")
                
            messagebox.showinfo("Очистка", f"Удалено файлов: {count}\nПоля очищены.")

    def _create_passport(self):
        text = self.txt_output.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Нет данных", "Сначала выполните шифрование.")
            return
        try:
            data = {
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "algorithm": "AES-256 (StdLib)",
                "integrity": "HMAC-SHA256",
                "output_hash": hashlib.sha256(text.encode()).hexdigest()[:12]
            }
            # 🔹 Имя файла с датой
            now = datetime.now().strftime("%Y-%m-%d_%H-%M")
            path = os.path.join(self.CACHE_DIR, f"passport_{now}.json")
            with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)
            messagebox.showinfo("Готово", f"Паспорт сохранен:\n{path}")
        except Exception as e: messagebox.showerror("Ошибка", str(e))

    def _select_cover_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.bmp")])
        if path:
            self.stego_cover_path.set(path)
            self.cover_drop_zone.config(text=f"✅ {os.path.basename(path)}", bg="#d5f5e3", fg="#27ae60")
            self.cover_path_label.config(text=path, fg="#27ae60")

    def _select_secret_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.bmp")])
        if path:
            self.stego_secret_path.set(path)
            self.secret_drop_zone.config(text=f"✅ {os.path.basename(path)}", bg="#fadbd8", fg="#c0392b")
            self.secret_path_label.config(text=path, fg="#c0392b")

def run():
    if TKDND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    
    app = EncryptionApp(root)
    root.mainloop()

if __name__ == "__main__":
    run()