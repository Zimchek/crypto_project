"""
Модульные тесты для системы логирования.
Запуск: pytest tests/test_logger.py -v
"""
import pytest
import sys
import os
import tempfile
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Импортируем класс логгера из app.py или вынеси его в отдельный файл
from gui.app import ActivityLogger


class TestActivityLogger:
    """Тесты для класса ActivityLogger"""

    @pytest.fixture
    def temp_log_dir(self):
        """Создаёт временную папку для логов"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_log_file_created_with_header(self, temp_log_dir):
        """Тест: файл лога создаётся с заголовком"""
        logger = ActivityLogger(temp_log_dir)
        
        assert os.path.exists(logger.log_path), "Файл лога не создан"
        
        with open(logger.log_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "CRYPTO PROJECT" in content or "ACTIVITY LOG" in content
        assert "Date:" in content

    def test_log_entry_format(self, temp_log_dir):
        """Тест: формат записи в логе [HH:MM:SS] message"""
        logger = ActivityLogger(temp_log_dir)
        logger.log("TEST_ACTION")
        
        with open(logger.log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Ищем нашу запись
        test_lines = [l for l in lines if "TEST_ACTION" in l]
        assert len(test_lines) > 0, "Запись не найдена в логе"
        
        # Проверяем формат времени [12:34:56]
        import re
        assert re.search(r'\[\d{2}:\d{2}:\d{2}\]', test_lines[0]), "Неверный формат времени"

    def test_multiple_logs_append(self, temp_log_dir):
        """Тест: несколько записей добавляются, а не перезаписывают"""
        logger = ActivityLogger(temp_log_dir)
        
        logger.log("ACTION_1")
        logger.log("ACTION_2")
        logger.log("ACTION_3")
        
        with open(logger.log_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert content.count("ACTION_1") == 1
        assert content.count("ACTION_2") == 1
        assert content.count("ACTION_3") == 1

    def test_log_section_separator(self, temp_log_dir):
        """Тест: разделитель секции"""
        logger = ActivityLogger(temp_log_dir)
        logger.log_section("TEST_SECTION")
        
        with open(logger.log_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "TEST_SECTION" in content
        assert "-" * 10 in content  # Разделитель из дефисов