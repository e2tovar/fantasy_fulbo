from typing import List
import pandas as pd

from config.settings import WEEK_PATH
from utils.get_data_from_excel import read_excel_teams_results, read_excel_players
from utils.save_week import save_week_players_stats_from_df, save_week_team_stats_from_df, save_week_team_result_from_df

from database.player_statistics import PlayerStatisticsManager
from database.team_results import TeamResultsManager
from database.team_stats import TeamStatsManager


class WeekDataManager:
    def __init__(self, file_path: str, year: int, season: str, match_week: int):
        self.file_path = file_path
        self.year = year
        self.season = season
        self.match_week = match_week
        self.trm = TeamResultsManager()
        self.tsm = TeamStatsManager()

    def upload_week(self):
        """
        Carga los datos de la jornada. Esta es una función crucial
        """
        # Load teams results
        df_resultado, df_stats = read_excel_teams_results(self.file_path)

        # Add metadata to DataFrames
        df_stats['year'] = self.year
        df_stats['season'] = self.season
        df_stats['match_week'] = self.match_week

        df_resultado['match_week'] = self.match_week
        df_resultado['year'] = self.year
        df_resultado['season'] = self.season

        # Save data using the manager instances
        save_week_team_result_from_df(df_resultado, self.trm)
        save_week_team_stats_from_df(df_stats, self.tsm)

        print(f"Team results for week {self.match_week} for season {self.season} loaded successfully.")

    @staticmethod
    def calcular_ranking(jugadores: List):
        return sorted(jugadores, key=lambda x: x.puntos, reverse=True)


if __name__ == "__main__":
    file_path = WEEK_PATH
    year = 2025
    season = 1
    match_week = 1

    week_data_manager = WeekDataManager(file_path, year, season, match_week)
    week_data_manager.upload_week()