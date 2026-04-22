"""
Модульные тесты для модуля стеганографии.
Запуск: pytest tests/test_stego.py -v
"""
import pytest
import sys
import os
import tempfile
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crypto_core.stego_service import StegoService


class TestStegoService:
    """Тесты для класса StegoService"""

    @pytest.fixture
    def temp_png(self):
        """Создаёт временное PNG-изображение для тестов"""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            # Создаём простое изображение 100x100 RGB
            img = Image.new("RGB", (100, 100), color=(128, 64, 200))
            img.save(tmp.name, format="PNG")
            yield tmp.name
            # Cleanup
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

    def test_hide_and_extract_roundtrip(self, temp_png):
        """Тест: спрятать и извлечь текст"""
        secret_text = "Секретное сообщение для стеганографии 🔐"
        key = "stego_test_key"
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as out:
            output_path = out.name
        
        try:
            # Прячем
            result = StegoService.hide_encrypted_text(secret_text, key, temp_png, output_path)
            assert result["status"] == "success"
            assert os.path.exists(output_path)
            
            # Извлекаем
            extract_result = StegoService.extract_and_decrypt(output_path, key)
            assert extract_result["status"] == "success"
            assert extract_result["decrypted_text"] == secret_text
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_wrong_key_fails_extraction(self, temp_png):
        """Тест: неверный ключ при извлечении"""
        secret = "Hidden message"
        key_correct = "correct"
        key_wrong = "wrong"
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as out:
            output_path = out.name
        
        try:
            StegoService.hide_encrypted_text(secret, key_correct, temp_png, output_path)
            
            with pytest.raises(ValueError, match="ключ|Key|ошибка|Ошибка"):
                StegoService.extract_and_decrypt(output_path, key_wrong)
                
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_empty_inputs_raise_error(self, temp_png):
        """Тест: пустые входные данные"""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as out:
            output_path = out.name
        
        try:
            with pytest.raises(ValueError):
                StegoService.hide_encrypted_text("", "key", temp_png, output_path)
            
            with pytest.raises(ValueError):
                StegoService.hide_encrypted_text("text", "", temp_png, output_path)
                
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_nonexistent_image_raises_error(self):
        """Тест: несуществующее изображение"""
        with pytest.raises(FileNotFoundError):
            StegoService.hide_encrypted_text("text", "key", "nonexistent.png", "out.png")