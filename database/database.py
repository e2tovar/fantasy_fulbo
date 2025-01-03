import sqlite3
import sqlalchemy


class DatabaseManager:
    def __init__(self):
        self.connection = sqlite3.connect("data/fantasy.db")
        self.engine = sqlalchemy.create_engine("sqlite:///data/fantasy.db")
        self.cursor = self.connection.cursor()

    def __enter__(self):
        return self.cursor

    def __exit__(self):
        self.connection.commit()
        self.connection.close()

    def execute_query(self, query, params=()):
        self.cursor.execute(query, params)
        self.connection.commit()

    def fetch_query(self, query, params=()):
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        return results

    def delete_table(self, table_name):
        self.execute_query(f"DROP TABLE IF EXISTS {table_name}")
