import base64
import os
from datetime import datetime
from .engines.base import BaseCipher

#(XOR + base64 для вывода в GUI)
class XorCipher(BaseCipher):
    @staticmethod
    def encrypt(plaintext: str, key: str) -> str:
        if not key:
            raise ValueError("Ключ не может быть пустым")
        key_bytes = key.encode()
        pt_bytes = plaintext.encode()
        enc_bytes = bytes([p ^ key_bytes[i % len(key_bytes)] for i, p in enumerate(pt_bytes)])
        return base64.b64encode(enc_bytes).decode()

    @staticmethod
    def decrypt(ciphertext: str, key: str) -> str:
        if not key:
            raise ValueError("Ключ не может быть пустым")
        try:
            raw_bytes = base64.b64decode(ciphertext)
        except Exception:
            raise ValueError("Некорректный формат шифротекста (должен быть Base64)")
        key_bytes = key.encode()
        dec_bytes = bytes([c ^ key_bytes[i % len(key_bytes)] for i, c in enumerate(raw_bytes)])
        return dec_bytes.decode()

# 🌟 Публичная точка входа для "подвязки как у АС"
class CryptoService:
    """Единственный класс, который импортируют внешние системы."""
    _engine = XorCipher()  # Можно менять на AES, GOST, RSA и т.д.

    @classmethod
    def set_engine(cls, engine: BaseCipher):
        cls._engine = engine

    @classmethod
    def encrypt(cls, text: str, key: str) -> str:
        return cls._engine.encrypt(text, key)

    @classmethod
    def decrypt(cls, text: str, key: str) -> str:
        return cls._engine.decrypt(text, key)
class CryptoService:
    _engine = XorCipher()

    @classmethod
    def set_engine(cls, engine: BaseCipher):
        cls._engine = engine

    @classmethod
    def encrypt(cls, text: str, key: str) -> str:
        return cls._engine.encrypt(text, key)

    @classmethod
    def decrypt(cls, text: str, key: str) -> str:
        return cls._engine.decrypt(text, key)
    
    # === Новые методы для работы с файлами ===
    
    @classmethod
    def encrypt_file(cls, input_path: str, output_path: str, key: str) -> dict:
        """
        Шифрует файл и сохраняет результат.
        Возвращает метаданные операции.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Файл не найден: {input_path}")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            plaintext = f.read()
        
        ciphertext = cls.encrypt(plaintext, key)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ciphertext)
        
        return {
            "input_file": input_path,
            "output_file": output_path,
            "original_size": len(plaintext),
            "encrypted_size": len(ciphertext),
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    
    @classmethod
    def decrypt_file(cls, input_path: str, output_path: str, key: str) -> dict:
        """
        Дешифрует файл и сохраняет результат.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Файл не найден: {input_path}")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            ciphertext = f.read()
        
        plaintext = cls.decrypt(ciphertext, key)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(plaintext)
        
        return {
            "input_file": input_path,
            "output_file": output_path,
            "decrypted_size": len(plaintext),
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }