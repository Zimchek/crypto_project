"""
Менеджер базы данных аудита (SQLite) - Работает на любом ПК без установки!
"""
import sqlite3
import hashlib
from datetime import datetime
import os


class AuditDB:
    """Класс для работы с базой данных аудита операций (SQLite)"""
    
    def __init__(self, db_path: str = "audit.db"):
        """
        Инициализация подключения к локальной БД
        
        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path
        self.conn = None
        self.session_id = None
        
        # Если путь относительный, делаем его абсолютным (рядом с exe)
        if not os.path.isabs(self.db_path):
            if getattr(__import__('sys'), 'frozen', False):
                # Если запущено как .exe
                base_dir = os.path.dirname(__import__('sys').executable)
            else:
                # Если запущено как скрипт
                base_dir = os.path.abspath(os.path.dirname(__file__))
            self.db_path = os.path.join(base_dir, self.db_path)
            
        self._connect()
        self._init_tables()
        self._init_session()
    
    def _connect(self):
        """Устанавливает подключение к SQLite"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            print(f"✅ Подключено к локальной БД: {self.db_path}")
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            raise
    
    def _init_tables(self):
        """Создает таблицы, если их нет (Автоматически!)"""
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS Sessions (
                SessionID INTEGER PRIMARY KEY AUTOINCREMENT,
                StartedAt TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                EndedAt TEXT,
                AppVersion TEXT DEFAULT '1.0'
            );
            
            CREATE TABLE IF NOT EXISTS Operations (
                OperationID INTEGER PRIMARY KEY AUTOINCREMENT,
                SessionID INTEGER NOT NULL,
                Timestamp TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                OperationType TEXT NOT NULL,
                InputFile TEXT,
                OutputFile TEXT,
                Algorithm TEXT NOT NULL,
                Status TEXT NOT NULL CHECK(Status IN ('SUCCESS', 'FAILED')),
                ErrorDetails TEXT,
                KeyFingerprint TEXT,
                FOREIGN KEY (SessionID) REFERENCES Sessions(SessionID) ON DELETE CASCADE
            );
        """)
        self.conn.commit()
    
    def _init_session(self):
        """Регистрирует новый сеанс работы приложения"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO Sessions (AppVersion) VALUES (?)", ('1.0',))
            self.session_id = cursor.lastrowid
            self.conn.commit()
            print(f"📋 Начат сеанс работы (ID: {self.session_id})")
        except Exception as e:
            print(f"⚠️ Не удалось создать сеанс: {e}")
    
    def log_operation(self, operation_type: str, algorithm: str, status: str,
                      input_file: str = None, output_file: str = None,
                      key: str = None, error: str = None):
        """Записывает операцию в базу данных"""
        if not self.session_id:
            return
        
        key_fingerprint = None
        if key:
            key_fingerprint = hashlib.sha256(key.encode()).hexdigest()[:16]
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO Operations 
                (SessionID, OperationType, Algorithm, Status, InputFile, OutputFile, KeyFingerprint, ErrorDetails)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.session_id, operation_type, algorithm, status,
                input_file, output_file, key_fingerprint, error
            ))
            self.conn.commit()
        except Exception as e:
            print(f"⚠️ Ошибка записи в БД: {e}")
            self.conn.rollback()
    
    def close(self):
        """Завершает сеанс и закрывает подключение"""
        if self.session_id and self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("UPDATE Sessions SET EndedAt = datetime('now', 'localtime') WHERE SessionID = ?", 
                               (self.session_id,))
                self.conn.commit()
                print(f"✅ Сеанс {self.session_id} завершён")
            except Exception as e:
                print(f"⚠️ Ошибка завершения сеанса: {e}")
        
        if self.conn:
            self.conn.close()
            print("🔌 Подключение к БД закрыто")
    
    def get_statistics(self):
        """Получает статистику операций"""
        if not self.conn:
            return {}
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as TotalOperations,
                    SUM(CASE WHEN Status = 'SUCCESS' THEN 1 ELSE 0 END) as SuccessCount,
                    SUM(CASE WHEN Status = 'FAILED' THEN 1 ELSE 0 END) as FailedCount
                FROM Operations WHERE SessionID = ?
            """, (self.session_id,))
            
            stats = cursor.fetchone()
            return {
                'total': stats['TotalOperations'],
                'success': stats['SuccessCount'],
                'failed': stats['FailedCount']
            }
        except Exception as e:
            return {}