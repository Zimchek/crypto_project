import base64

class BaseCipher:
    """Базовый класс шифра"""
    
    @staticmethod
    def encrypt(plaintext: str, key: str) -> str:
        raise NotImplementedError
        
    @staticmethod
    def decrypt(ciphertext: str, key: str) -> str:
        raise NotImplementedError