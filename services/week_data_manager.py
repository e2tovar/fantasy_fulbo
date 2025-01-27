import logging
import pandas as pd

from utils.get_data_from_excel import read_excel_teams_results, read_excel_players_stats
from utils.get_data_from_app import scrap_app_week_data

from database.player_statistics import PlayerStatisticsManager
from database.team_results import TeamResultsManager
from database.team_stats import TeamStatsManager
from database.players import PlayerManager


class WeekDataManager:
    def __init__(self, year: int, season: str, match_week: int, week_note: str = '', file=None):
        self.year = year
        self.season = season
        self.match_week = match_week
        self.week_note = week_note
        self.trm = TeamResultsManager()
        self.tsm = TeamStatsManager()
        self.psm = PlayerStatisticsManager()
        self.file_path = self._build_path(file)

    def _build_path(self, file):
        if file:
            return file
        return f"data/jornadas/{self.year}/result_season_{self.season}_week_{self.match_week}.xlsx"

    def __save_week_team_stats_from_df(self, df: pd.DataFrame, tsm: TeamStatsManager) -> None:
        """
        Save team statistics from a DataFrame to a TeamStatsManager.

        :param df: DataFrame containing team statistics.
        :param tsm: Instance of TeamStatsManager.
        """
        required_columns = {tsm.YEAR, tsm.SEASON, tsm.MATCH_WEEK, tsm.TEAM, tsm.GOALS, tsm.GOALS_AGAINST,
                            tsm.POINTS, tsm.POSITION}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"DataFrame is missing required columns: {required_columns - set(df.columns)}")

        try:
            tsm.add_team_stats_week(df)
        except Exception as e:
            logging.error(f"Error saving team stats batch: {e}")

    def __save_week_team_result_from_df(self, df: pd.DataFrame, trm: TeamResultsManager) -> None:
        """
        Save team results from a DataFrame to a TeamResultsManager.

        :param df: DataFrame containing match data.
        :param trm: Instance of TeamResultsManager.
        """
        required_columns = {trm.GAME_NUMBER, trm.YEAR, trm.SEASON, trm.MATCH_WEEK, trm.LOCAL, trm.AWAY,
                            trm.LOCAL_GOALS, trm.AWAY_GOALS}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"DataFrame is missing required columns: {required_columns - set(df.columns)}")

        try:
            trm.add_team_results_week(df)
        except Exception as e:
            logging.error(f"Error saving team results batch: {e}")

    def __save_week_player_stats_from_df(self, df: pd.DataFrame, psm: PlayerStatisticsManager) -> None:
        """
        Save player statistics from a DataFrame to a PlayerStatisticsManager.

        :param df: DataFrame containing player statistics.
        :param psm: Instance of PlayerStatisticsManager.
        """
        required_columns = {
            psm.PLAYER_ID,
            psm.YEAR,
            psm.SEASON,
            psm.MATCH_WEEK,
            psm.DATE,
            psm.TEAM,
            psm.GOALS,
            psm.OWN_GOALS,
            psm.ASSISTS,
            psm.MVP,
            psm.MEDIA,
            psm.YELLOW_CARD,
            psm.RED_CARD,
            psm.VOTES,
            psm.TOTAL_VOTES,
            psm.NOTE
            }
        if not required_columns.issubset(df.columns):
            raise ValueError(f"DataFrame is missing required columns: {required_columns - set(df.columns)}")

        # get only required columns
        df = df[list(required_columns)]

        try:
            psm.add_player_statistics_week_from_df(df)
        except Exception as e:
            logging.error(f"Error saving player statistics batch: {e}")

    def upload_week(self) -> None:
        """
        Carga los datos de la jornada. Esta es una función crucial
        """
        df_resultado, df_stats = self.__read_team_data()
        df_players = self.__read_player_data()

        self.__save_week_team_result_from_df(df_resultado, self.trm)
        self.__save_week_team_stats_from_df(df_stats, self.tsm)
        self.__save_week_player_stats_from_df(df_players, self.psm)

        logging.info(f"Team results for week {self.match_week} for season {self.season} loaded successfully.")

    def __read_team_data(self):
        df_resultado, df_stats = read_excel_teams_results(self.file_path)
        df_stats['year'] = self.year
        df_stats['season'] = self.season
        df_stats['match_week'] = self.match_week
        df_resultado['match_week'] = self.match_week
        df_resultado['year'] = self.year
        df_resultado['season'] = self.season
        return df_resultado, df_stats

    def __read_player_data(self) -> pd.DataFrame:
        logger = logging.getLogger(__name__)

        # From excel
        try:
            df_excel = read_excel_players_stats(self.file_path)
        except Exception as e:
            logger.exception(f"Failed to read player data from Excel: {e}")
            df_excel = pd.DataFrame()

        # from app
        try:
            df_app = scrap_app_week_data(
                stats_year=self.year, stats_season=self.season, stats_week=self.match_week, note=self.week_note)
        except Exception as e:
            logger.exception(f"Failed to scrape player data from app: {e}")
            df_app = pd.DataFrame()

        # mapping to id
        pm = PlayerManager()
        excel_map = pm.excel_name_id_map
        app_map = pm.app_name_id_map
        df_excel['player_id'] = df_excel['name'].map(excel_map)
        df_app['player_id'] = df_app['name'].map(app_map)
        df_app.drop(columns=['name'], inplace=True)

        # merge
        df_players = pd.merge(df_excel, df_app, on=['player_id'], how='outer', validate='one_to_one')
        if df_players['player_id'].isnull().any():
            raise ValueError("Merged data contains missing player IDs.")

        df_players['note'] = self.week_note

        return df_players

    def delete_week(self) -> None:
        """
        Elimina los datos de la jornada.
        """
        self.trm.delete_week_results(self.year, self.season, self.match_week)
        self.tsm.delete_week_stats(self.year, self.season, self.match_week)
