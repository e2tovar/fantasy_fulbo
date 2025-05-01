import logging
import pandas as pd

from utils.get_data_from_excel import read_excel_teams_results, read_excel_players_stats
from utils.vars import meses_a_numero

from database.player_statistics import PlayerStatisticsManager
from database.team_results import TeamResultsManager
from database.team_stats import TeamStatsManager
from database.players import PlayerManager


class WeekDataManager:
    def __init__(self, year: int, season: str, match_week: int, match_date: str,
                 trm: TeamResultsManager, tsm: TeamStatsManager, psm: PlayerStatisticsManager, pm: PlayerManager,
                 week_note: str = '', file=None, autogol_players=None):
        self.year = year
        self.season = season
        self.match_week = match_week
        self.match_date = match_date
        self.week_note = week_note
        self.trm = trm
        self.tsm = tsm
        self.psm = psm
        self.pm = pm
        self.file_path = self._build_path(file)
        self.file_name = file.name.split('.')[0]
        self.excel_names_map = {}
        self.autogol_players = autogol_players

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
                            tsm.POINTS, tsm.POSITION, tsm.WINS, tsm.DRAWS, tsm.DEFEATS}
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

    def update_week(self) -> None:
        """
        Carga los datos de la jornada. Esta es una función crucial
        """

        # match_day = self.file_name.split('-')[0].zfill(2)
        # match_month = meses_a_numero[self.file_name.split('-')[1]].zfill(2)
        # match_year = self.year

        df_resultado, df_stats = self.__read_team_data()
        df_players = self.__read_player_data()

        # add dates
        df_players['year'] = self.year
        df_players['season'] = self.season
        df_players['match_week'] = self.match_week
        df_players['date'] = self.match_date

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
            df_excel = read_excel_players_stats(self.file_path, self.autogol_players)
        except Exception as e:
            logger.exception(f"Failed to read player data from Excel: {e}")
            df_excel = pd.DataFrame()

        # mapping to id
        df_excel['name'] = df_excel['name'].replace(self.excel_names_map)
        df_excel['player_id'] = df_excel['name'].map(self.pm.excel_name_id_map)
        df_excel['note'] = self.week_note

        return df_excel

    def delete_week(self) -> None:
        """
        Elimina los datos de la jornada.
        """
        self.trm.delete_week_results(self.year, self.season, self.match_week)
        self.tsm.delete_week_stats(self.year, self.season, self.match_week)
