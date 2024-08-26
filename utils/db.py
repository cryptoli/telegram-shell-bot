import sqlite3
from queue import Queue

class Database:
    def __init__(self, db_file='data/encrypted_db.sqlite', pool_size=5):
        self.db_file = db_file
        self.pool_size = pool_size
        self.connection_pool = Queue(maxsize=self.pool_size)
        
        # 初始化连接池
        for _ in range(self.pool_size):
            conn = sqlite3.connect(self.db_file, check_same_thread=False)
            self.connection_pool.put(conn)
        
        self.create_tables()

    def create_tables(self):
        conn = self.get_connection()
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS servers (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                alias TEXT,
                                host TEXT,
                                username TEXT,
                                password TEXT,
                                port INTEGER,
                                key_data TEXT,
                                UNIQUE(user_id, host))''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON servers (user_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_alias ON servers (alias)')
        self.release_connection(conn)

    def get_connection(self):
        """
        从连接池中获取连接。
        """
        return self.connection_pool.get()

    def release_connection(self, conn):
        """
        将连接放回连接池。
        """
        self.connection_pool.put(conn)

    def add_server(self, user_id, alias, host, username, password, port=22, key_data=None):
        conn = self.get_connection()
        with conn:
            conn.execute('INSERT OR REPLACE INTO servers (user_id, alias, host, username, password, port, key_data) VALUES (?, ?, ?, ?, ?, ?, ?)',
                         (user_id, alias, host, username, password, port, key_data))
        self.release_connection(conn)

    def remove_server(self, user_id, alias):
        conn = self.get_connection()
        with conn:
            conn.execute('DELETE FROM servers WHERE user_id=? AND alias=?', (user_id, alias))
        self.release_connection(conn)

    def get_servers(self, user_id):
        conn = self.get_connection()
        with conn:
            result = conn.execute('SELECT * FROM servers WHERE user_id=?', (user_id,)).fetchall()
        self.release_connection(conn)
        return result

    def get_server(self, user_id, alias):
        conn = self.get_connection()
        with conn:
            result = conn.execute('SELECT * FROM servers WHERE user_id=? AND alias=?', (user_id, alias)).fetchone()
        self.release_connection(conn)
        return result

    def close_all_connections(self):
        """
        关闭连接池中的所有连接。
        """
        while not self.connection_pool.empty():
            conn = self.connection_pool.get()
            conn.close()


