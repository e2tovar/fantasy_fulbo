from typing import List
import pandas as pd

from config.settings import WEEK_PATH
from utils.get_data_from_excel import read_excel_teams_results, read_excel_players

from database.player_statistics import PlayerStatisticsManager
from database.team_results import TeamResultsManager
from database.team_stats import TeamStatsManager
from database.players import PlayerManager


class WeekDataManager:
    def __init__(self, file_path: str, year: int, season: str, match_week: int):
        self.file_path = file_path
        self.year = year
        self.season = season
        self.match_week = match_week
        self.trm = TeamResultsManager()
        self.tsm = TeamStatsManager()

    def __save_week_team_stats_from_df(self, df: pd.DataFrame, tsm: TeamStatsManager) -> None:
        """
        Save team statistics from a DataFrame to a TeamStatsManager.

        :param df: DataFrame containing team statistics.
        :param tsm: Instance of TeamStatsManager.
        """
        required_columns = {tsm.YEAR, tsm.SEASON, tsm.MATCH_WEEK, tsm.TEAM_NAME, tsm.GOALS, tsm.GOALS_AGAINST,
                            tsm.POINTS, tsm.RANK}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"DataFrame is missing required columns: {required_columns - set(df.columns)}")

        stats = [
            (row['year'], row['season'], row['match_week'], row['team'], row['goals'], row['goals_against'],
                row['points'], row['rank'])
            for _, row in df.iterrows()
        ]
        try:
            tsm.add_team_stats_week(stats)
        except Exception as e:
            print(f"Error saving team stats batch: {e}")

    def __save_week_team_result_from_df(self, df: pd.DataFrame, trm: TeamResultsManager) -> None:
        """
        Save team results from a DataFrame to a TeamResultsManager.

        :param df: DataFrame containing match data.
        :param trm: Instance of TeamResultsManager.
        """
        required_columns = {trm.GAME_NUMBER, trm.YEAR, trm.SEASON, trm.MATCH_WEEK, trm.LOCAL_NAME, trm.AWAY_NAME,
                            trm.LOCAL_GOALS, trm.AWAY_GOALS}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"DataFrame is missing required columns: {required_columns - set(df.columns)}")

        results = [
            (row['game_number'],
                row['year'],
                row['season'],
                row['match_week'],
                row['local'],
                row['away'],
                row['local_goals'],
                row['away_goals'])
            for _, row in df.iterrows()
        ]
        try:
            trm.add_team_results_week(results)
        except Exception as e:
            print(f"Error saving team results batch: {e}")

    def __save_week_player_excel_stats_from_df(self, df: pd.DataFrame, psm: PlayerStatisticsManager) -> None:
        """
        Save player statistics from a DataFrame to a PlayerStatisticsManager.

        :param df: DataFrame containing player statistics.
        :param psm: Instance of PlayerStatisticsManager.
        """
        required_columns = {psm.PLAYER_ID, psm.YEAR, psm.SEASON, psm.MATCH_WEEK, psm.TEAM, psm.DATE, psm.GOALS,
                            psm.ASSISTS, psm.MEDIA, psm.MVP, psm.YELLOW_CARD, psm.RED_CARD, psm.VOTES, psm.TOTAL_VOTES,
                            psm.NOTE}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"DataFrame is missing required columns: {required_columns - set(df.columns)}")

    def upload_week(self):
        """
        Carga los datos de la jornada. Esta es una función crucial
        """
        # TEAMS
        df_resultado, df_stats = read_excel_teams_results(self.file_path)

        # Add metadata to DataFrames
        df_stats['year'] = self.year
        df_stats['season'] = self.season
        df_stats['match_week'] = self.match_week

        df_resultado['match_week'] = self.match_week
        df_resultado['year'] = self.year
        df_resultado['season'] = self.season

        # Save data using the manager instances
        self.__save_week_team_result_from_df(df_resultado, self.trm)
        self.__save_week_team_stats_from_df(df_stats, self.tsm)

        # PLAYERS
        df_players = read_excel_players(self.file_path)
        # map excel names to id
        pm = PlayerManager()
        players_map = pm._excel_name_id_map()
        df_players['id'] = df_players['name'].map(players_map)
        df_players.drop(columns=['name'], inplace=True)
        df_players['match_week'] = self.match_week
        df_players['year'] = self.year
        df_players['season'] = self.season

        # TODO save players

        print(f"Team results for week {self.match_week} for season {self.season} loaded successfully.")

    def delete_week(self):
        """
        Elimina los datos de la jornada.
        """
        self.trm.delete_week_results(self.year, self.season, self.match_week)
        self.tsm.delete_week_stats(self.year, self.season, self.match_week)


if __name__ == "__main__":
    file_path = WEEK_PATH
    year = 2025
    season = 1
    match_week = 1

    week_data_manager = WeekDataManager(file_path, year, season, match_week)
    week_data_manager.upload_week()
