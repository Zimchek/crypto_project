"""
Модульные тесты для криптографического модуля.
Запуск: pytest tests/test_crypto.py -v
"""
import pytest
import sys
import os

# Добавляем корень проекта в путь для импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crypto_core import CryptoService


class TestCryptoService:
    """Тесты для класса CryptoService"""

    def test_encrypt_decrypt_roundtrip_ru(self):
        """Тест: шифрование и расшифрование русского текста"""
        plaintext = "Привет, мир! Это тестовое сообщение 🛡️"
        key = "my_secret_key_2026"
        
        encrypted = CryptoService.encrypt(plaintext, key)
        decrypted = CryptoService.decrypt(encrypted, key)
        
        assert decrypted == plaintext, "Расшифрованный текст не совпадает с исходным"
        assert isinstance(encrypted, str), "Зашифрованный результат должен быть строкой"
        assert len(encrypted) > len(plaintext), "Зашифрованный текст должен быть длиннее"

    def test_encrypt_decrypt_roundtrip_long(self):
        """Тест: работа с длинным текстом"""
        plaintext = "A" * 10000  # 10 тысяч символов
        key = "long_test_key"
        
        encrypted = CryptoService.encrypt(plaintext, key)
        decrypted = CryptoService.decrypt(encrypted, key)
        
        assert decrypted == plaintext

    def test_different_keys_produce_different_output(self):
        """Тест: разные ключи дают разный результат"""
        text = "Secret message"
        key1 = "key_one"
        key2 = "key_two"
        
        enc1 = CryptoService.encrypt(text, key1)
        enc2 = CryptoService.encrypt(text, key2)
        
        assert enc1 != enc2, "Разные ключи должны давать разный шифротекст"

    def test_same_text_different_encryption(self):
        """Тест: один текст с тем же ключом шифруется по-разному (из-за соли)"""
        text = "Same text"
        key = "same_key"
        
        enc1 = CryptoService.encrypt(text, key)
        enc2 = CryptoService.encrypt(text, key)
        
        assert enc1 != enc2, "Шифрование должно использовать случайную соль"
        
        # Но оба должны расшифровываться в исходный текст
        assert CryptoService.decrypt(enc1, key) == text
        assert CryptoService.decrypt(enc2, key) == text

    def test_wrong_key_raises_error(self):
        """Тест: неверный ключ вызывает ошибку"""
        text = "Secret"
        key_correct = "correct_key"
        key_wrong = "wrong_key"
        
        encrypted = CryptoService.encrypt(text, key_correct)
        
        with pytest.raises(ValueError, match="ЦЕЛОСТНОСТЬ|Неверный ключ|ошибка"):
            CryptoService.decrypt(encrypted, key_wrong)

    def test_empty_key_raises_error(self):
        """Тест: пустой ключ вызывает ошибку"""
        with pytest.raises(ValueError):
            CryptoService.encrypt("text", "")
        
        with pytest.raises(ValueError):
            CryptoService.decrypt("data", "")

    def test_empty_plaintext_raises_error(self):
        """Тест: пустой текст для шифрования вызывает ошибку"""
        with pytest.raises(ValueError):
            CryptoService.encrypt("", "key")

    def test_invalid_base64_raises_error(self):
        """Тест: некорректный Base64 в шифротексте"""
        with pytest.raises(ValueError, match="Base64|некорректный|формат"):
            CryptoService.decrypt("!!!not-valid-base64!!!", "key")

    def test_corrupted_ciphertext_raises_error(self):
        """Тест: повреждённый шифротекст"""
        valid_enc = CryptoService.encrypt("test", "key")
        corrupted = valid_enc[:-5] + "XXXXX"  # Повреждаем конец
        
        with pytest.raises(ValueError):
            CryptoService.decrypt(corrupted, "key")

    def test_special_characters_handling(self):
        """Тест: обработка специальных символов и эмодзи"""
        test_cases = [
            "Test with symbols: !@#$%^&*()",
            "Unicode: Привет 🌍 مرحبا 你好",
            "Newlines:\nTabs:\tBackslash:\\",
            "Quotes: 'single' and \"double\"",
        ]
        key = "special_test_key"
        
        for text in test_cases:
            encrypted = CryptoService.encrypt(text, key)
            decrypted = CryptoService.decrypt(encrypted, key)
            assert decrypted == text, f"Failed for: {repr(text)}"