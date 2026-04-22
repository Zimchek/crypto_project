# 🛡️ CryptoProject Pro

**Современное приложение для шифрования данных и стеганографии**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📥 Скачать

### Готовое приложение (Windows)
[⬇️ Скачать CryptoProject_v1.exe]([https://github.com/ТВОЙ_НИК/Zimchek/releases/download/v1.0/CryptoProject_v1.exe](https://github.com/Zimchek/CryptoProject))

> **Размер:** ~45 MB | **Версия:** 1.0 | **Требования:** Windows 7 и выше

---

## ✨ Возможности

### 🔐 Криптография
- **AES-256 шифрование** с использованием стандартной библиотеки Python
- **HMAC-SHA256** для проверки целостности данных
- **PBKDF2** с 100,000 итераций для генерации ключа
- Шифрование и дешифрование текста в один клик

### 🖼️ Стеганография
- Скрытие зашифрованного текста в изображениях **PNG/BMP**
- Метод **LSB** (Least Significant Bit) — невидимое внедрение
- **Drag-and-drop** поддержка для удобной работы с картинками
- Двойная защита: шифрование + скрытие

### 📊 Логирование
- Автоматическая запись всех действий пользователя
- Временные метки для каждого события
- История сессий с датой и временем
- Логи сохраняются в `cache/logs/`

### 💻 Интерфейс
- Современный GUI на **tkinter**
- Поддержка перетаскивания файлов
- Прокрутка для удобной работы
- Кнопки быстрого доступа

---

## 🚀 Установка

### Вариант 1: Готовое приложение (рекомендуется)
1. Скачайте `CryptoProject.exe` из раздела [Releases](https://github.com/ТВОЙ_НИК/Zimchek/releases)
2. Запустите файл
3. Готово! Установка не требуется

### Вариант 2: Из исходного кода
```bash
# Клонируйте репозиторий
git clone https://github.com/ТВОЙ_НИК/Zimchek.git
cd Zimchek

# Создайте виртуальное окружение
python -m venv venv

# Активируйте его
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Запустите приложение
python main.py
