import sqlite3
import os

class Database:
    def __init__(self, db_file='data/encrypted_db.sqlite'):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS servers (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                host TEXT,
                                username TEXT,
                                password TEXT,
                                port INTEGER,
                                key_data TEXT,
                                UNIQUE(user_id, host))''')
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON servers (user_id)')
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_host ON servers (host)')

    def add_server(self, user_id, host, username, password, port=22, key_data=None):
        with self.conn:
            self.conn.execute('INSERT OR REPLACE INTO servers (user_id, host, username, password, port, key_data) VALUES (?, ?, ?, ?, ?, ?)',
                              (user_id, host, username, password, port, key_data))

    def remove_server(self, user_id, host):
        with self.conn:
            self.conn.execute('DELETE FROM servers WHERE user_id=? AND host=?', (user_id, host))

    def get_servers(self, user_id):
        with self.conn:
            return self.conn.execute('SELECT * FROM servers WHERE user_id=?', (user_id,)).fetchall()

    def get_server(self, user_id, host):
        with self.conn:
            return self.conn.execute('SELECT * FROM servers WHERE user_id=? AND host=?', (user_id, host)).fetchone()
