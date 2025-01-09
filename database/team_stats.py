from .database import DatabaseManager


class TeamStatsManager(DatabaseManager):
    # Define constants for column names
    ID = "id"
    YEAR = "year"
    SEASON = "season"
    MATCH_WEEK = "match_week"
    TEAM_NAME = "team_name"
    GOALS = "goals"
    GOALS_AGAINST = "goals_against"
    POINTS = "points"
    RANK = "rank"

    def create_table(self):
        self.execute_query(f"""
            CREATE TABLE IF NOT EXISTS team_stats(
                {self.ID} INTEGER PRIMARY KEY AUTOINCREMENT,
                {self.YEAR} INTEGER NOT NULL,
                {self.SEASON} INTEGER NOT NULL,
                {self.MATCH_WEEK} INTEGER NOT NULL,
                {self.TEAM_NAME} VARCHAR(10),
                {self.GOALS} INTEGER,
                {self.GOALS_AGAINST} INTEGER,
                {self.POINTS} INTEGER,
                {self.RANK} INTEGER
            )
        """)

    def delete_table(self):
        return super().delete_table("team_stats")

    def add_team_stats(self, year, season, match_week, team_name, goals, goals_against, points, rank):
        # Delete first if exists
        query = f"""
            DELETE FROM team_stats
            WHERE {self.YEAR} = ? AND {self.SEASON} = ? AND {self.MATCH_WEEK} = ? AND {self.TEAM_NAME} = ?
        """
        self.execute_query(query, (year, season, match_week, team_name))

        self.execute_query(f"""
            INSERT INTO team_stats
            ({self.YEAR},
            {self.SEASON},
            {self.MATCH_WEEK},
            {self.TEAM_NAME},
            {self.GOALS},
            {self.GOALS_AGAINST},
            {self.POINTS}, {self.RANK})
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (year, season, match_week, team_name, goals, goals_against, points, rank))

    def add_team_stats_week(self, stats):
        """
        Add multiple team statistics in a single batch operation.

        :param stats: List of tuples,
        each containing (year, season, match_week, team_name, goals, goals_against, points, rank)
        """

        # Validate results structure and data types
        for stat in stats:
            if not isinstance(stat, tuple) or len(stat) != 8:
                raise ValueError("Each result must be a tuple with 8 elements.")
            if not all(isinstance(field, (int, str)) for field in stat):
                raise TypeError("Each field in the result tuple must be of type int or str.")

        # Delete existing results for the same match to avoid duplicates
        self.delete_week_stats(stat[0], stat[1], stat[2])

        query = f"""
            INSERT INTO team_stats
            ({self.YEAR},
            {self.SEASON},
            {self.MATCH_WEEK},
            {self.TEAM_NAME},
            {self.GOALS},
            {self.GOALS_AGAINST},
            {self.POINTS},
            {self.RANK})
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_queries(query, stats)

    def get_week_stats(self, year, season, match_week):
        return self.fetch_query(f"""
            SELECT * FROM team_stats
            WHERE {self.YEAR} = ? AND {self.SEASON} = ? AND {self.MATCH_WEEK} = ?
        """, (year, season, match_week))

    def delete_week_stats(self, year, season, match_week):
        self.execute_query(f"""
            DELETE FROM team_stats
            WHERE {self.YEAR} = ? AND {self.SEASON} = ? AND {self.MATCH_WEEK} = ?
        """, (year, season, match_week))

    def delete_season_stats(self, year, season):
        print(f"Deleting season {year} - {season}")
        self.execute_query(f"""
            DELETE FROM team_stats
            WHERE {self.YEAR} = ? AND {self.SEASON} = ?
        """, (year, season))

    def delete_team_stats(self, year, season, match_week, team_name):
        self.execute_query(f"""
            DELETE FROM team_stats
            WHERE {self.YEAR} = ? AND {self.SEASON} = ? AND {self.MATCH_WEEK} = ? AND {self.TEAM_NAME} = ?
        """, (year, season, match_week, team_name))
