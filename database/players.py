from .database import DatabaseManager
import pandas as pd
from functools import lru_cache

class PlayerManager(DatabaseManager):
    # Define class-level constants for column names
    ID = "id"
    EXCEL_NAME = "excel_name"
    PLAYER_NAME = "player_name"
    POSITION = "field_position"
    POSITION_SHORT = "field_position_short"
    PRICE = "price"

    def __init__(self):
        super().__init__()
        # Pre-fetch and cache the mappings
        self.excel_name_id_map = self._fetch_excel_name_id_map()
        self.excel_names = self.excel_name_id_map.keys()
        self.app_name_id_map = self._fetch_app_name_id_map()

    @lru_cache(maxsize=1)
    def _fetch_excel_name_id_map(self):
        query = f"SELECT {self.EXCEL_NAME}, {self.ID} FROM players"
        try:
            players = self.fetch_query(query)
            return {player[0]: player[1] for player in players}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {}

    def _fetch_app_name_id_map(self):
        query = f"SELECT {self.PLAYER_NAME}, {self.ID} FROM players"
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
                {self.EXCEL_NAME} TEXT NOT NULL,
                {self.PLAYER_NAME} TEXT NOT NULL,
                {self.POSITION} TEXT NOT NULL,
                {self.POSITION_SHORT} TEXT NOT NULL,
                {self.PRICE} REAL NOT NULL
            )
        """)

    def add_player(self, excel_name, player_name, field_position):
        allowed_positions = {"Delantero", "Mediocampista", "Defensor"}
        if field_position not in allowed_positions:
            raise ValueError(f"Invalid position: {field_position}")

        map_position_short = {"Delantero": "DEL", "Mediocampista": "MED", "Defensor": "DEF"}
        position_short = map_position_short[field_position]

        query = f"INSERT INTO players({self.EXCEL_NAME}, {self.PLAYER_NAME}, {self.POSITION}, {self.POSITION_SHORT}) VALUES (?, ?, ?, ?) RETURNING {self.ID}"
        id = self.execute_query(query, (excel_name, player_name, field_position, position_short))
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
