from .database import DatabaseManager
import pandas as pd


class PlayerStatisticsManager(DatabaseManager):
    # Define class-level constants for column names
    ID = "id"
    PLAYER_ID = "player_id"
    YEAR = "year"
    SEASON = "season"
    MATCH_WEEK = "match_week"
    DATE = "date"
    TEAM = "team"
    GOALS = "goals"
    ASSISTS = "assists"
    MVP = "mvp"
    MEDIA = "media"
    YELLOW_CARD = "yellow_card"
    RED_CARD = "red_card"
    VOTES = "votes"
    TOTAL_VOTES = "total_votes"
    NOTE = "note"

    def create_table(self):
        self.execute_query(f"""
            CREATE TABLE IF NOT EXISTS player_statistics (
                {self.ID} INTEGER PRIMARY KEY AUTOINCREMENT,
                {self.PLAYER_ID} INTEGER NOT NULL,
                {self.YEAR} INTEGER NOT NULL,
                {self.SEASON} INTEGER NOT NULL,
                {self.MATCH_WEEK} INTEGER NOT NULL,
                {self.DATE} DATE,
                {self.TEAM} VARCHAR,
                {self.GOALS} INTEGER NOT NULL,
                {self.ASSISTS} INTEGER NOT NULL,
                {self.MVP} INTEGER NOT NULL,
                {self.MEDIA} FLOAT NOT NULL,
                {self.YELLOW_CARD} INTEGER NOT NULL,
                {self.RED_CARD} INTEGER NOT NULL,
                {self.VOTES} INTEGER NOT NULL,
                {self.TOTAL_VOTES} INTEGER NOT NULL,
                {self.NOTE} TEXT,
                FOREIGN KEY ({self.PLAYER_ID}) REFERENCES player(id)
            )
        """)

    def add_player_statistics(self, player_id, year, season, match_week, date, team, goals, assists, mvp, media, yellow_card, red_card, votes, total_votes, note):
        # Delete first if exists
        query = f"DELETE FROM player_statistics WHERE {self.PLAYER_ID} = ? AND {self.YEAR} = ? AND {self.SEASON} = ? AND {self.MATCH_WEEK} = ?"
        self.execute_query(query, (player_id, year, season, match_week))
        query = f"""
            INSERT INTO player_statistics ({self.PLAYER_ID}, {self.YEAR}, {self.SEASON}, {self.MATCH_WEEK}, {self.DATE}, {self.TEAM}, {self.GOALS}, {self.ASSISTS}, {self.MVP},
            {self.MEDIA}, {self.YELLOW_CARD}, {self.RED_CARD}, {self.VOTES}, {self.TOTAL_VOTES}, {self.NOTE})
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.execute_query(query, (player_id, year, season, match_week, date, team, goals, assists, mvp, media, yellow_card, red_card, votes, total_votes, note))

    def get_general_statistics(self):
        query = f"""
            SELECT
                player.name AS player_name,
                SUM(ps.{self.GOALS}) AS goles,
                SUM(ps.{self.ASSISTS}) AS asistencias,
                ROUND(AVG(ps.{self.MEDIA}),2) AS media,
                SUM(ps.{self.MVP}) AS mvp,
                SUM(ps.{self.YELLOW_CARD}) AS amarillas,
                SUM(ps.{self.RED_CARD}) AS rojas
            FROM player_statistics ps
            JOIN players ON ps.{self.PLAYER_ID} = player.id
            GROUP BY player.id
            ORDER BY goles DESC
        """
        return pd.read_sql_query(query, self.engine, index_col='player_name')

    def get_week(self, week):
        query = f"""
            SELECT player.name, ps.{self.GOALS}, ps.{self.ASSISTS}
            FROM player_statistics ps
            JOIN players ON ps.{self.PLAYER_ID} = players.id
            WHERE ps.{self.MATCH_WEEK} = ?"""

        return self.fetch_query(query, (week,))
