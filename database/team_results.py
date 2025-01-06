from .database import DatabaseManager
import pandas as pd


class TeamResultsManager(DatabaseManager):
    def create_table(self):
        # playerstable. Total Statistics
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS team_results(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                season INTEGER NOT NULL,
                match_week INTEGER NOT NULL,
                team_name VARCHAR(10),
                goals INTEGER,
                goals_against INTEGER,
                points INTEGER,
                rank INTEGER
            )
        """)

    def delete_table(self):
        return super().delete_table("team_results")

    def add_team_result(self, year, season, match_week, team_name, goals, goals_against, points, rank):
        # Delete first if exists
        query = """
            DELETE FROM team_results
            WHERE year = ? AND season = ? AND match_week = ? AND team_name = ?
        """
        self.execute_query(query, (year, season, match_week, team_name))

        self.execute_query("""
            INSERT INTO team_results
            (year, season, match_week, team_name, goals, goals_against, points, rank)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (year, season, match_week, team_name, goals, goals_against, points, rank))

    def get_week_result(self, year, season, match_week):
        return self.fetch_query("""
            SELECT * FROM team_results
            WHERE year = ? AND season = ? AND match_week = ?
        """, (year, season, match_week))

    def delete_week_result(self, year, season, match_week):
        self.execute_query("""
            DELETE FROM team_results
            WHERE year = ? AND season = ? AND match_week = ?
        """, (year, season, match_week))

    def delete_season_results(self, year, season):
        print(f"Deleting season {year} - {season}")
        self.execute_query("""
            DELETE FROM team_results
            WHERE year = ? AND season = ?
        """, (year, season))
