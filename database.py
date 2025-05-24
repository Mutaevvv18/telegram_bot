import sqlite3
from typing import Optional


class Database:
    def __init__(self, db_name: str = 'weather_bot.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Таблица пользователей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            username TEXT,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Таблица поисковых запросов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS searches (
            search_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            city TEXT,
            search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')

        # Таблица фотографий
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            photo_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            file_id TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')

        self.conn.commit()

    def add_user(self, user_id: int, first_name: str, username: Optional[str]):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, first_name, username)
        VALUES (?, ?, ?)
        ''', (user_id, first_name, username))
        self.conn.commit()

    def add_search(self, user_id: int, city: str):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO searches (user_id, city)
        VALUES (?, ?)
        ''', (user_id, city))
        self.conn.commit()

    def add_photo(self, user_id: int, file_id: str):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO photos (user_id, file_id)
        VALUES (?, ?)
        ''', (user_id, file_id))
        self.conn.commit()

    def get_user_searches(self, user_id: int) -> list:
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT city, COUNT(*) as count 
        FROM searches 
        WHERE user_id = ?
        GROUP BY city
        ORDER BY count DESC
        LIMIT 5
        ''', (user_id,))
        return cursor.fetchall()

    def close(self):
        self.conn.close()