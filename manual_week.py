from services.week_data_manager import WeekDataManager
from config.settings import WEEK_PATH

file_path = WEEK_PATH
year = 2025
season = 1
match_week = 1

week_data_manager = WeekDataManager(file_path, year, season, match_week)
week_data_manager.upload_week()