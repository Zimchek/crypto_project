import base64
import os
import hashlib
from .engines.base import BaseCipher

try:
    from Crypto.Cipher import AES
    from Crypto.Protocol.KDF import PBKDF2
    from Crypto.Util.Padding import pad, unpad
    from Crypto.Random import get_random_bytes
except ImportError:
    raise ImportError(
        "Установите pycryptodome: pip install pycryptodome"
    )


class AESCipher(BaseCipher):
    """
    AES-256-CBC шифрование с PBKDF2 для генерации ключа.
    Стандарт индустрии, криптостойкий алгоритм.
    """
    
    KEY_LENGTH = 32  # 256 бит = 32 байта
    IV_LENGTH = 16   # 128 бит = 16 байт (размер блока AES)
    SALT_LENGTH = 16
    
    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        """
        Генерирует криптографически стойкий ключ из пароля
        с использованием PBKDF2 (100,000 итераций).
        """
        return PBKDF2(
            password,
            salt,
            dkLen=AESCipher.KEY_LENGTH,
            count=100000  # Количество итераций для защиты от перебора
        )
    
    @staticmethod
    def encrypt(plaintext: str, key: str) -> str:
        """
        Шифрование AES-256-CBC.
        
        Формат результата:
        base64(salt + iv + ciphertext)
        
        Args:
            plaintext: Исходный текст
            key: Пароль/ключ (любой длины)
        
        Returns:
            Base64-строка с зашифрованными данными
        """
        if not key:
            raise ValueError("Ключ не может быть пустым")
        if not plaintext:
            raise ValueError("Текст не может быть пустым")
        
        # Генерируем случайную соль и IV для КАЖДОГО шифрования
        salt = get_random_bytes(AESCipher.SALT_LENGTH)
        iv = get_random_bytes(AESCipher.IV_LENGTH)
        
        # Получаем ключ из пароля
        derived_key = AESCipher._derive_key(key, salt)
        
        # Создаём AES-шифр в режиме CBC
        cipher = AES.new(derived_key, AES.MODE_CBC, iv)
        
        # Шифруем с добавлением padding (PKCS7)
        plaintext_bytes = plaintext.encode('utf-8')
        padded_data = pad(plaintext_bytes, AES.block_size)
        ciphertext = cipher.encrypt(padded_data)
        
        # Объединяем salt + iv + ciphertext и кодируем в Base64
        result = salt + iv + ciphertext
        return base64.b64encode(result).decode('utf-8')
    
    @staticmethod
    def decrypt(ciphertext: str, key: str) -> str:
        """
        Дешифрование AES-256-CBC.
        
        Args:
            ciphertext: Base64-строка от encrypt()
            key: Тот же пароль, что использовался при шифровании
        
        Returns:
            Расшифрованный текст
        """
        if not key:
            raise ValueError("Ключ не может быть пустым")
        if not ciphertext:
            raise ValueError("Шифротекст не может быть пустым")
        
        try:
            # Декодируем Base64
            raw_data = base64.b64decode(ciphertext)
        except Exception:
            raise ValueError("Некорректный формат шифротекста (должен быть Base64)")
        
        # Проверяем минимальную длину (salt + iv минимум)
        if len(raw_data) < (AESCipher.SALT_LENGTH + AESCipher.IV_LENGTH):
            raise ValueError("Шифротекст слишком короткий")
        
        # Извлекаем salt, iv и ciphertext
        salt = raw_data[:AESCipher.SALT_LENGTH]
        iv = raw_data[AESCipher.SALT_LENGTH:AESCipher.SALT_LENGTH + AESCipher.IV_LENGTH]
        encrypted_data = raw_data[AESCipher.SALT_LENGTH + AESCipher.IV_LENGTH:]
        
        # Получаем тот же ключ из пароля и соли
        derived_key = AESCipher._derive_key(key, salt)
        
        # Создаём шифр для расшифровки
        cipher = AES.new(derived_key, AES.MODE_CBC, iv)
        
        try:
            # Расшифровываем и убираем padding
            padded_plaintext = cipher.decrypt(encrypted_data)
            plaintext = unpad(padded_plaintext, AES.block_size)
            return plaintext.decode('utf-8')
        except ValueError as e:
            # Ошибка padding = неверный ключ или повреждённые данные
            raise ValueError("Неверный ключ или повреждённый шифротекст")
        except Exception as e:
            raise ValueError(f"Ошибка расшифровки: {str(e)}")


# 🌟 Публичная точка входа для "подвязки как у АС"
class CryptoService:
    """
    Единый интерфейс для криптографических операций.
    Внешние системы работают только с этим классом.
    """
    _engine = AESCipher()  # По умолчанию используем AES

    @classmethod
    def set_engine(cls, engine: BaseCipher):
        """Заменить алгоритм шифрования (для тестов или смены алгоритма)"""
        cls._engine = engine

    @classmethod
    def encrypt(cls, text: str, key: str) -> str:
        """Зашифровать текст"""
        return cls._engine.encrypt(text, key)

    @classmethod
    def decrypt(cls, text: str, key: str) -> str:
        """Расшифровать текст"""
        return cls._engine.decrypt(text, key)