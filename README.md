# 🛡️ CryptoProject Pro

> **Современное приложение для шифрования данных и стеганографии на Python**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/Zimchek/CryptoProject)](https://github.com/Zimchek/CryptoProject/releases)

---

## 📥 Скачать

### 🪟 Готовое приложение для Windows
[⬇️ Скачать CryptoProject v1.2 (.exe)](https://github.com/Zimchek/CryptoProject/releases/download/v1.2/CryptoProject_v1.2.exe)

| Параметр | Значение |
|----------|----------|
| **Версия** | 1.2 (Stable) |
| **Размер** | ~45 MB |
| **ОС** | Windows 7/8/10/11 |
| **Установка** | Не требуется (портативное) |

---

## ✨ Возможности

### 🔐 Криптография
- **AES-256-GCM** — стойкое симметричное шифрование
- **HMAC-SHA256** — проверка целостности данных
- **PBKDF2** (100,000 итераций) — защита ключа от перебора
- Работа только на **стандартной библиотеке** (без тяжелых зависимостей)

### 🖼️ Стеганография
- Скрытие зашифрованного текста в изображениях **PNG/BMP**
- Алгоритм **LSB** (Least Significant Bit) — невидимое внедрение
- **Drag-and-drop** поддержка для удобной работы с файлами
- **Двойная защита**: сначала шифруем, потом прячем

### 💻 Интерфейс и удобство
- Современный графический интерфейс на `tkinter`
- Поддержка перетаскивания файлов (Drag-and-Drop)
- Прокрутка контента и адаптивный дизайн
- Криптопаспорт: автоматическая генерация отчёта об операции

### 📊 Логирование и аудит
- Автоматическая запись всех действий пользователя
- Временные метки для каждого события
- **Автономная БД SQLite** (`audit.db`) для структурированного аудита
- Логи **не удаляются** при очистке кеша

---

## 🚀 Быстрый старт

### Вариант 1: Готовое приложение (рекомендуется)
1. Скачайте [CryptoProject_v1.2.exe](https://github.com/Zimchek/CryptoProject/releases/download/v1.2/CryptoProject_v1.2.exe)
2. Запустите файл двойным кликом
3. При первом запуске автоматически создадутся:
   - Папка `cache/` для временных файлов
   - Файл `audit.db` для журнала операций
4. Готово! Установка не требуется.

### Вариант 2: Запуск из исходного кода
```bash
# 1. Клонируйте репозиторий
git clone https://github.com/Zimchek/CryptoProject.git
cd CryptoProject

# 2. Создайте виртуальное окружение
python -m venv venv

# 3. Активируйте его
# Для Windows:
venv\Scripts\activate
# Для Linux/Mac:
source venv/bin/activate

# 4. Установите зависимости
pip install -r requirements.txt

# 5. Запустите приложение
python main.py
