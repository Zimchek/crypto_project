import os
from stegano import lsb
from PIL import Image
import sys

# Добавляем путь для импорта CryptoService
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from crypto_core import CryptoService


class StegoService:
    """
    Сервис стеганографии: скрывает зашифрованный текст в изображениях.
    Использует метод LSB (Least Significant Bit).
    """

    @staticmethod
    def hide_encrypted_text(text: str, key: str, cover_image_path: str, output_path: str) -> dict:
        """
        Шифрует текст и прячет его в изображение.
        
        Args:
            text: Исходный текст
            key: Ключ шифрования
            cover_image_path: Путь к исходной картинке (контейнер)
            output_path: Путь для сохранения результата
        
        Returns:
            dict с метаданными операции
        """
        if not os.path.exists(cover_image_path):
            raise FileNotFoundError(f"Изображение не найдено: {cover_image_path}")
        
        if not text or not key:
            raise ValueError("Текст и ключ обязательны")
        
        # Проверяем формат изображения
        try:
            img = Image.open(cover_image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
        except Exception as e:
            raise ValueError(f"Не удалось открыть изображение: {str(e)}")
        
        # 1. Шифруем текст через AES
        encrypted_text = CryptoService.encrypt(text, key)
        
        # 2. Прячем зашифрованный текст в изображение (LSB метод)
        secret_image = lsb.hide(cover_image_path, encrypted_text)
        
        # 3. Сохраняем результат
        secret_image.save(output_path, format='PNG')
        
        # Получаем размеры для отчёта
        original_size = os.path.getsize(cover_image_path)
        result_size = os.path.getsize(output_path)
        
        return {
            "status": "success",
            "original_image": cover_image_path,
            "output_image": output_path,
            "original_size_kb": round(original_size / 1024, 2),
            "result_size_kb": round(result_size / 1024, 2),
            "encrypted_text_length": len(encrypted_text),
            "message": f"Текст зашифрован и спрятан в {output_path}"
        }

    @staticmethod
    def extract_and_decrypt(secret_image_path: str, key: str) -> dict:
        """
        Извлекает скрытый текст из изображения и расшифровывает его.
        
        Args:
            secret_image_path: Путь к изображению со скрытыми данными
            key: Ключ дешифрования
        
        Returns:
            dict с расшифрованным текстом и метаданными
        """
        if not os.path.exists(secret_image_path):
            raise FileNotFoundError(f"Изображение не найдено: {secret_image_path}")
        
        if not key:
            raise ValueError("Ключ обязателен")
        
        try:
            # 1. Извлекаем скрытое сообщение из изображения
            hidden_data = lsb.reveal(secret_image_path)
            
            if not hidden_data:
                raise ValueError("В изображении не найдены скрытые данные")
            
            # 2. Расшифровываем данные
            decrypted_text = CryptoService.decrypt(hidden_data, key)
            
            return {
                "status": "success",
                "decrypted_text": decrypted_text,
                "hidden_data_length": len(hidden_data),
                "decrypted_length": len(decrypted_text),
                "message": "Данные успешно извлечены и расшифрованы"
            }
            
        except ValueError as e:
            if "INCORRECT" in str(e) or "padding" in str(e).lower():
                raise ValueError("Неверный ключ или повреждённое изображение")
            raise
        except Exception as e:
            raise ValueError(f"Ошибка извлечения данных: {str(e)}")

    @staticmethod
    def check_image_has_data(image_path: str) -> bool:
        """
        Проверяет, есть ли в изображении скрытые данные.
        (Технически stegano не предоставляет прямого способа проверить без извлечения)
        """
        try:
            # Пытаемся извлечь - если получится, значит данные есть
            lsb.reveal(image_path)
            return True
        except:
            return False