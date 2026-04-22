"""
Менеджер базы данных аудита (SQL Server)
"""
import pyodbc
import hashlib
from datetime import datetime
import os


class AuditDB:
    """Класс для работы с базой данных аудита операций"""
    
    def __init__(self, server: str = "localhost", database: str = "CryptoAudit"):
        """
        Инициализация подключения к БД
        
        Args:
            server: Имя сервера SQL Server
            database: Имя базы данных
        """
        self.server = server
        self.database = database
        self.conn = None
        self.session_id = None
        self._connect()
        self._init_session()
    
    def _connect(self):
        """Устанавливает подключение к SQL Server"""
        try:
            # Строка подключения для Windows Authentication
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Trusted_Connection=yes;"
                f"TrustServerCertificate=yes;"
            )
            
            self.conn = pyodbc.connect(connection_string)
            self.conn.autocommit = False  # Используем транзакции
            print(f"✅ Подключено к БД: {self.database} на сервере {self.server}")
            
        except pyodbc.Error as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            print("💡 Убедитесь, что SQL Server запущен и доступен")
            raise
    
    def _init_session(self):
        """Регистрирует новый сеанс работы приложения"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO dbo.Sessions (AppVersion) VALUES (?)
            """, ('1.0',))
            
            self.session_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]
            self.conn.commit()
            print(f"📋 Начат сеанс работы (ID: {self.session_id})")
            
        except Exception as e:
            print(f"⚠️ Не удалось создать сеанс: {e}")
            self.conn.rollback()
    
    def log_operation(self, operation_type: str, algorithm: str, status: str,
                      input_file: str = None, output_file: str = None,
                      key: str = None, error: str = None):
        """
        Записывает операцию в базу данных
        
        Args:
            operation_type: Тип операции (ENCRYPT, DECRYPT, STEGO_HIDE, STEGO_EXTRACT)
            algorithm: Использованный алгоритм
            status: Статус (SUCCESS, FAILED)
            input_file: Входной файл (опционально)
            output_file: Выходной файл (опционально)
            key: Ключ шифрования (сохраняется только хеш)
            error: Текст ошибки (если status=FAILED)
        """
        if not self.session_id:
            print("⚠️ Сеанс не инициализирован, логирование пропущено")
            return
        
        # Создаём отпечаток ключа (никогда не храним сам ключ!)
        key_fingerprint = None
        if key:
            key_fingerprint = hashlib.sha256(key.encode()).hexdigest()[:16]
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO dbo.Operations 
                (SessionID, OperationType, Algorithm, Status, InputFile, OutputFile, KeyFingerprint, ErrorDetails)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.session_id,
                operation_type,
                algorithm,
                status,
                input_file,
                output_file,
                key_fingerprint,
                error
            ))
            
            self.conn.commit()
            
        except Exception as e:
            print(f"⚠️ Не удалось записать операцию в БД: {e}")
            self.conn.rollback()
    
    def close(self):
        """Завершает сеанс и закрывает подключение"""
        if self.session_id and self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    UPDATE dbo.Sessions 
                    SET EndedAt = SYSDATETIME() 
                    WHERE SessionID = ?
                """, (self.session_id,))
                
                self.conn.commit()
                print(f"✅ Сеанс {self.session_id} завершён")
                
            except Exception as e:
                print(f"⚠️ Ошибка при завершении сеанса: {e}")
                self.conn.rollback()
        
        if self.conn:
            self.conn.close()
            print("🔌 Подключение к БД закрыто")
    
    def get_statistics(self):
        """
        Получает статистику операций
        
        Returns:
            dict со статистикой
        """
        if not self.conn:
            return {}
        
        try:
            cursor = self.conn.cursor()
            
            # Общая статистика
            cursor.execute("""
                SELECT 
                    COUNT(*) as TotalOperations,
                    SUM(CASE WHEN Status = 'SUCCESS' THEN 1 ELSE 0 END) as SuccessCount,
                    SUM(CASE WHEN Status = 'FAILED' THEN 1 ELSE 0 END) as FailedCount
                FROM dbo.Operations
                WHERE SessionID = ?
            """, (self.session_id,))
            
            stats = cursor.fetchone()
            
            return {
                'total': stats.TotalOperations,
                'success': stats.SuccessCount,
                'failed': stats.FailedCount
            }
            
        except Exception as e:
            print(f"⚠️ Не удалось получить статистику: {e}")
            return {}