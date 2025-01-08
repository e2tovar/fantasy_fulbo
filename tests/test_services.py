import unittest
from unittest.mock import patch
import pandas as pd

from services import upload_week


class TestLoadWeek(unittest.TestCase):
    @patch('services.read_excel_teams_results')
    @patch('services.save_week_team_stats_from_df')
    def test_load_week(self, mock_save_week_team_stats_from_df, mock_read_excel_teams_results):
        # Mock the return value of read_excel_teams_results
        mock_read_excel_teams_results.return_value = (pd.DataFrame(), pd.DataFrame())

        # Call the function with test data
        file_path = 'data/test_file.xlsx'
        year = 2025
        season = 21
        match_week = 1

        upload_week(file_path, year, season, match_week)

        # Assert that read_excel_teams_results was called with the correct file path
        mock_read_excel_teams_results.assert_called_once_with(file_path)

        # Assert that save_week_team_stats_from_df was called
        self.assertTrue(mock_save_week_team_stats_from_df.called)

        # Assert that the DataFrame has the correct columns
        df_stats = mock_save_week_team_stats_from_df.call_args[0][0]
        self.assertIn('year', df_stats.columns)
        self.assertIn('season', df_stats.columns)
        self.assertIn('match_week', df_stats.columns)

if __name__ == '__main__':
    unittest.main()