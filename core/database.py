import sqlite3

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def create_tables(self):
        """创建数据库表。"""
        if not self.conn:
            raise RuntimeError("数据库未连接。请先调用 connect() 方法。")
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL,
            features BLOB
        )
        ''')
        self.conn.commit()

    def commit(self):
        """提交事务"""
        if self.conn:
            self.conn.commit()

    def connect(self):
        """连接到SQLite数据库。"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        """关闭数据库连接。"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def execute_query(self, query, params=()):
        """执行SQL查询并返回结果。

        参数:
            query (str): SQL查询语句。
            params (tuple): 查询参数。

        返回:
            list: 查询结果。
        """
        if not self.conn:
            raise RuntimeError("数据库未连接。请先调用 connect() 方法。")
        

        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        self.conn.commit()
        return results