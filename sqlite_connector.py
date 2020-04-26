import sqlite3


class SQLiteAPI:
    def __init__(self):
        self.conn = sqlite3.connect('sqlite3.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_all_tables(self):
        self.create_table_users()

    def create_table_users(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            user_id INTEGER PRIMARY KEY,
                            username VARCHAR(255) NOT NULL,
                            password VARCHAR(255) NOT NULL,
                            UNIQUE (username)
                            )''')

    def add_user(self, username, password):
        try:
            self.cursor.execute("""INSERT INTO users (username, password) VALUES (?, ?)""",
                                (username, password))
            print(self.cursor.fetchall())
            self.conn.commit()
            return True
        except Exception as error:
            print('------')
            print(error)
            return False

    def check_user(self, username, password):
        self.cursor.execute("""SELECT username FROM users WHERE username=? AND password=?""",
                            (username, password))
        return self.cursor.fetchall()
