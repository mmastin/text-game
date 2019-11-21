import sqlite3
from sqlite3 import Error


class dbConnector:
    def __init__(self):
        self.database = "textgame.db"
        self.conn = None

    def connect_with_cursor(self):
        self.conn = sqlite3.connect(self.database)
        cursor = self.conn.cursor()
        return cursor

    def close(self):
        self.conn.close()
        self.conn = None
        return "Closed Connection"
    
    def create_room_table(self):
        c = self.connect_with_cursor()
        sql = """CREATE TABLE players
        (id integer PRIMARY KEY AUTOINCREMENT,
        location integer)"""
        c.execute(sql)
        self.conn.commit()
        self.close()

    def add_player(self):
        c = self.connect_with_cursor()
        sql = """INSERT INTO players(location)
            VALUES(?) """
        c.execute(sql, (0,))
        self.conn.commit()
        p_id = c.lastrowid
        self.close()
        return p_id



    
        