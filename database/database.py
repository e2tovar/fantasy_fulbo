import sqlite3
import sqlalchemy


class DatabaseManager:
    def __init__(self):
        self.con_path = "data/fantasy.db"
        self.engine = sqlalchemy.create_engine("sqlite:///data/fantasy.db")

    def execute_query(self, query, params=()):
        connection = sqlite3.connect(self.con_path)
        cursor = connection.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        connection.commit()
        cursor.close()
        connection.close()
        return results

    def execute_queries(self, query, params=()):
        connection = sqlite3.connect(self.con_path)
        cursor = connection.cursor()
        cursor.executemany(query, params)
        connection.commit()
        cursor.close()
        connection.close()

    def fetch_query(self, query, params=()):
        connection = sqlite3.connect(self.con_path)
        cursor = connection.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results

    def delete_table(self, table_name):
        self.execute_query(f"DROP TABLE IF EXISTS {table_name}")
