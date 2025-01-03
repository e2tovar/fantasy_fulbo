from .database import DatabaseManager
import pandas as pd


class PlayerManager(DatabaseManager):
    def create_table(self):
        # playerstable. Total Statistics
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS players(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                name_fantasy TEXT NO NULL,
                position TEXT NOT NULL,
                price REAL NOT NULL
            )
        """)

    def delete_table(self):
        return super().delete_table("players")

    def get_fantasy_id(self):
        """
        Devuelve un diccionario con el mapeo de cada jugador y su ID
        """
        query = "SELECT name, id FROM players"
        players = self.fetch_query(query)
        return {players[0]: players[1] for players in players}

    def add_player(self, name, name_fantasy, position, price):
        query = "INSERT INTO players(name, name_fantasy, position, price) VALUES (?, ?, ?, ?)"
        self.execute_query(query, (name, name_fantasy, position, price))

    def get_player(self) -> pd.DataFrame:
        query = "SELECT * FROM players"
        return pd.read_sql_query(sql=query, con=self.engine, index_col="id")

    def update_player_price(self, player_id, price):
        query = """
            UPDATE players
            SET price = ?
            WHERE id = ?
        """
        self.execute_query(query, (price, player_id))

    def delete_player(self, player_id):
        query = "DELETE FROM players WHERE id = ?"
        self.execute_query(query, (player_id,))
