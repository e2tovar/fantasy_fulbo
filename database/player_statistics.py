from .database import DatabaseManager
import pandas as pd


class PlayerStatisticsManager(DatabaseManager):
    def create_table(self):
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS player_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                seasson INTEGER NOT NULL,
                match_week INTEGER NOT NULL,
                date DATE,
                team VARCHAR,
                goals INTEGER NOT NULL,
                assists INTEGER NOT NULL,
                mvp INTEGER NOT NULL,
                media FLOAT NOT NULL,
                yellow_card INTEGER NOT NULL,
                red_card INTEGER NOT NULL,
                votes INTEGER NOT NULL,
                total_votes INTEGER NOT NULL,
                note TEXT,
                FOREIGN KEY (player_id) REFERENCES player(id)
            )
        """)

    def delete_table(self):
        self.execute_query("DROP TABLE IF EXISTS player_statistics")

    def add_player_statistics(
            self, player_id, year, seasson, match_week, date, team, goals, assists, mvp, media, yellow_card,
            red_card, votes, total_votes, note):
        # Delete first if exists
        query = "DELETE FROM player_statistics WHERE player_id = ? AND year = ? AND seasson = ? AND match_week = ?"
        self.execute_query(query, (player_id, year, seasson, match_week))
        query = """
            INSERT INTO player_statistics (player_id, year, seasson, match_week, date, team, goals, assists, mvp,
            media, yellow_card, red_card, votes, total_votes, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.execute_query(
            query, (player_id, year, seasson, match_week, date, team, goals, assists, mvp, media, yellow_card,
                    red_card, votes, total_votes, note))

    def get_general_statistics(self):
        """
        Retrieve aggregated statistics (goals, assists, etc.)
        for a specific year and season.
        """
        query = """
            SELECT
                player.name AS player_name,
                SUM(ps.goals) AS goles,
                SUM(ps.assists) AS asistencias,
                ROUND(AVG(ps.media),2) AS media,
                SUM(ps.mvp) AS mvp,
                SUM(ps.yellow_card) AS amarillas,
                SUM(ps.red_card) AS rojas
            FROM player_statistics ps
            JOIN players ON ps.player_id = player.id
            GROUP BY player.id
            ORDER BY goals DESC
        """
        return pd.read_sql_query(query, self.engine, index_col='player_name')

    def get_week(self, week):
        query = """
            SELECT player.name, ps.goals, ps.assists
            FROM player_statistics ps
            JOIN players ON ps.player_id = players.id
            WHERE ps.match_week = ?"""

        return self.fetch_query(query, (week,))
