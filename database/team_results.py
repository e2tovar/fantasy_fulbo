from .database import DatabaseManager


class TeamResultsManager(DatabaseManager):
    # Define constants for column names
    ID = "id"
    YEAR = "year"
    SEASON = "season"
    MATCH_WEEK = "match_week"
    GAME_NUMBER = "game_number"
    LOCAL = "local"
    AWAY = "away"
    away = "away"
    LOCAL_GOALS = "local_goals"
    AWAY_GOALS = "away_goals"

    def create_table(self):
        self.execute_query(f"""
            CREATE TABLE IF NOT EXISTS team_results (
                {self.ID} INTEGER PRIMARY KEY AUTOINCREMENT,
                {self.GAME_NUMBER} INTEGER NOT NULL,
                {self.YEAR} INTEGER NOT NULL,
                {self.SEASON} INTEGER NOT NULL,
                {self.MATCH_WEEK} INTEGER NOT NULL,
                {self.LOCAL} VARCHAR(50),
                {self.away} VARCHAR(50),
                {self.LOCAL_GOALS} INTEGER,
                {self.AWAY_GOALS} INTEGER
            )
        """)

    def delete_table(self):
        return super().delete_table("team_results")

    def add_team_result(self, game_number, year, season, match_week, local, away, local_goals, away_goals):
        # Delete existing result for the same match to avoid duplicates
        query = """
            DELETE FROM team_results
            WHERE year = ? AND season = ? AND match_week = ? AND game_number = ?
        """
        self.execute_query(query, (year, season, match_week, game_number))

        # Insert new result
        query = f"""
            INSERT INTO team_results
            ({self.GAME_NUMBER},
            {self.YEAR},
            {self.SEASON},
            {self.MATCH_WEEK},
            {self.LOCAL},
            {self.away},
            {self.LOCAL_GOALS},
            {self.AWAY_GOALS})
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_query(query, (game_number, year, season, match_week, local, away, local_goals, away_goals))

    def add_team_results_week(self, df):
        """
        Add multiple team results in a single batch operation.

        :param results: List of tuples, each containing (year, season, match_week, local, away, local_goals, away_goals)
        """

        results = [
            (row.game_number,
                row.year,
                row.season,
                row.match_week,
                row.local,
                row.away,
                row.local_goals,
                row.away_goals)
            for _, row in df.iterrows()
        ]

        # Validate results structure and data types
        for result in results:
            if not isinstance(result, tuple) or len(result) != 8:
                raise ValueError("Each result must be a tuple with 8 elements.")
            if not all(isinstance(field, (int, str)) for field in result):
                raise TypeError("Each field in the result tuple must be of type int or str.")

        # Delete existing results for the same match to avoid duplicates
        self.delete_week_results(result[1], result[2], result[3])

        query = f"""
            INSERT INTO team_results
            ({self.GAME_NUMBER},
            {self.YEAR},
            {self.SEASON},
            {self.MATCH_WEEK},
            {self.LOCAL},
            {self.away},
            {self.LOCAL_GOALS},
            {self.AWAY_GOALS})
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_queries(query, results)

    def get_week_results(self, year, season, match_week):
        query = f"""
            SELECT * FROM team_results
            WHERE {self.YEAR} = ? AND {self.SEASON} = ? AND {self.MATCH_WEEK} = ?
        """
        return self.fetch_query(query, (year, season, match_week))

    def delete_week_results(self, year, season, match_week):
        query = f"""
            DELETE FROM team_results
            WHERE {self.YEAR} = ? AND {self.SEASON} = ? AND {self.MATCH_WEEK} = ?
        """
        self.execute_query(query, (year, season, match_week))
