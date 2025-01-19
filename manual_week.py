from services.week_data_manager import WeekDataManager

year = 2025
season = 1
match_week = 3

week_data_manager = WeekDataManager(year, season, match_week)
week_data_manager.upload_week()
