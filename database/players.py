from .database import DatabaseManager
import pandas as pd


class PlayerManager(DatabaseManager):
    # Define class-level constants for column names
    ID = "id"
    NAME_EXCEL = "name_excel"
    NAME_APP = "name_app"
    POSITION = "position"
    PRICE = "price"

    def __init__(self):
        super().__init__()
        # Pre-fetch and cache the mappings
        self.excel_name_id_map = self._fetch_excel_name_id_map()
        self.app_name_id_map = self._fetch_app_name_id_map()

    def _fetch_excel_name_id_map(self):
        query = f"SELECT {self.NAME_EXCEL}, {self.ID} FROM players"
        try:
            players = self.fetch_query(query)
            return {player[0]: player[1] for player in players}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {}

    def _fetch_app_name_id_map(self):
        query = f"SELECT {self.NAME_APP}, {self.ID} FROM players"
        try:
            players = self.fetch_query(query)
            return {player[0]: player[1] for player in players}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {}

    def create_table(self):
        self.execute_query(f"""
            CREATE TABLE IF NOT EXISTS players(
                {self.ID} INTEGER PRIMARY KEY AUTOINCREMENT,
                {self.NAME_EXCEL} TEXT NOT NULL,
                {self.NAME_APP} TEXT NOT NULL,
                {self.POSITION} TEXT NOT NULL,
                {self.PRICE} REAL NOT NULL
            )
        """)

    def add_player(self, name, name_fantasy, position, price):
        allowed_positions = {"Delantero", "Mediocampo", "Defensor"}
        if price < 0:
            raise ValueError("Price cannot be negative")
        if position not in allowed_positions:
            raise ValueError(f"Invalid position: {position}")
        query = f"INSERT INTO players({self.NAME_EXCEL}, {self.NAME_APP}, {self.POSITION}, {self.PRICE}) VALUES (?, ?, ?, ?) RETURNING {self.ID}"
        id = self.execute_query(query, (name, name_fantasy, position, price))
        # Invalidate caches and refresh
        self.excel_name_id_map = self._fetch_excel_name_id_map()
        self.app_name_id_map = self._fetch_app_name_id_map()
        return id

    def update_player_price(self, player_id, price):
        if price < 0:
            raise ValueError("Price cannot be negative")
        query = f"""
            UPDATE players
            SET {self.PRICE} = ?
            WHERE {self.ID} = ?
        """
        self.execute_query(query, (price, player_id))
        # Invalidate caches and refresh
        self.excel_name_id_map = self._fetch_excel_name_id_map()
        self.app_name_id_map = self._fetch_app_name_id_map()

    def delete_player(self, player_id):
        query = f"DELETE FROM players WHERE {self.ID} = ?"
        self.execute_query(query, (player_id,))
        # Invalidate caches and refresh
        self.excel_name_id_map = self._fetch_excel_name_id_map()
        self.app_name_id_map = self._fetch_app_name_id_map()

    def get_all_players(self) -> pd.DataFrame:
        query = "SELECT * FROM players"
        return pd.read_sql_query(sql=query, con=self.engine, index_col=self.ID)

