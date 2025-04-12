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
    OWN_GOALS = "own_goals"
    ASSISTS = "assists"
    MVP = "mvp"
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
                {self.OWN_GOALS} INTEGER NOT NULL,
                {self.ASSISTS} INTEGER NOT NULL,
                {self.MVP} INTEGER NOT NULL,
                {self.YELLOW_CARD} INTEGER NOT NULL,
                {self.RED_CARD} INTEGER NOT NULL,
                {self.VOTES} INTEGER NOT NULL,
                {self.TOTAL_VOTES} INTEGER NOT NULL,
                {self.NOTE} TEXT,
                FOREIGN KEY ({self.PLAYER_ID}) REFERENCES player(id)
            )
        """)

    def add_player_statistics(self, player_id, year, season, match_week, date, team, goals, assists, mvp, yellow_card, red_card, votes, total_votes, note):
        # Delete first if exists
        query = f"DELETE FROM player_statistics WHERE {self.PLAYER_ID} = ? AND {self.YEAR} = ? AND {self.SEASON} = ? AND {self.MATCH_WEEK} = ?"
        self.execute_query(query, (player_id, year, season, match_week))
        query = f"""
            INSERT INTO player_statistics ({self.PLAYER_ID}, {self.YEAR}, {self.SEASON}, {self.MATCH_WEEK}, {self.DATE}, {self.TEAM}, {self.GOALS}, {self.ASSISTS}, {self.MVP},
            {self.YELLOW_CARD}, {self.RED_CARD}, {self.VOTES}, {self.TOTAL_VOTES}, {self.NOTE})
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.execute_query(query, (player_id, year, season, match_week, date, team, goals, assists, mvp, yellow_card, red_card, votes, total_votes, note))

    def add_player_statistics_week_from_df(self, df):
        """
        Add multiple player stats from the excel.
        :param results: List of tuples, each containing
        (player_id, year, season, match_week, date, team, goals, assists, mvp, yellow_card, red_card,
        votes, total_votes, note)
        """
        # Agregamos MVP a 0
        df['mvp'] = 0

        results = [
            (
                row.player_id,
                row.year,
                row.season,
                row.match_week,
                row.date,
                row.team,
                row.goals,
                row.own_goals,
                row.assists,
                row.note,
                row.mvp
            )
            for row in df.itertuples(index=False)
        ]

        # Validate results structure and data types
        for result in results:
            if not isinstance(result, tuple) or len(result) != 11:
                raise ValueError("Each result must be a tuple with 11 elements.")
            if not all(isinstance(field, (int, str)) for field in result):
                raise TypeError("Each field in the result tuple must be of type int or str.")

        # Collect unique (year, season, match_week) combinations to delete existing stats
        unique_weeks = set((result[1], result[2], result[3]) for result in results)
        for year, season, match_week in unique_weeks:
            self.delete_week_stats(year, season, match_week)

        # Prepare the query for inserting new statistics
        query = f"""
            INSERT INTO player_statistics
            ({self.PLAYER_ID},
             {self.YEAR},
             {self.SEASON},
             {self.MATCH_WEEK},
             {self.DATE},
             {self.TEAM},
             {self.GOALS},
             {self.OWN_GOALS},
             {self.ASSISTS},
             {self.NOTE},
             {self.MVP})
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_queries(query, results)

    def fetch_general_statistics(self, year, season):
        query = f"""
            SELECT
            pl.name_app AS nombre,
            pl.field_position_short as posicion_campo,
            SUM(ps.goals) AS goles,
            SUM(ps.assists) AS asistencias,
            SUM(ps.mvp) AS mvp,
            SUM(ts.goals) as goles_anotados_equipo,
            SUM(ts.goals_against) as goles_recibidos_equipo
        FROM player_statistics ps
        left JOIN players pl
            ON ps.player_id = pl.id
        left join team_stats ts
            ON ps.team = ts.team and ps.season = ts.season and ps.match_week = ts.match_week and ps.year = ts.year
        where ps.year = {year}
        and ps.season= {season}
        GROUP BY pl.id
        ORDER BY goles DESC
        """
        return pd.read_sql_query(query, self.engine, index_col='nombre')

    def get_week_statistics(self, year, season, match_week):
        query = f"""
        SELECT
            pl.name_app AS player_name,
            SUM(ps.goals) AS goles,
            SUM(ps.assists) AS asistencias,
            SUM(ps.mvp) AS mvp,
            SUM(ts.goals) as team_goals,
            SUM(ts.goals_against) as team_goals_against,
            ROUND(AVG(ts.goals_against),2) AS avg_team_goals_against
        FROM player_statistics ps
        left JOIN players pl
            ON ps.player_id = pl.id
        left join team_stats ts
            ON ps.team = ts.team and ps.season = ts.season and ps.year = ts.year and ps.match_week = ts.match_week
        where ps.year = {year}
        and ps.season = {season}
        and ps.match_week = {match_week}
        GROUP BY ps.player_id, ps.year, ps.season
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

    def fetch_last_year_season(self):
        query = """
        SELECT year, MAX(season)
        FROM player_statistics
        GROUP BY year
        ORDER BY year DESC
        LIMIT 1;
        """

        return self.fetch_query(query)

    def delete_week_stats(self, year, season, match_week):
        query = f"DELETE FROM player_statistics WHERE {self.YEAR} = ? AND {self.SEASON} = ? AND {self.MATCH_WEEK} = ?"
        self.execute_query(query, (year, season, match_week))
