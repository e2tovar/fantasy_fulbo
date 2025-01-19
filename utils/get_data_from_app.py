from services.scraping_bot import ScrapingBot


def scrap_app_week_data(stats_year, stats_season, stats_week, note=''):

    bot = ScrapingBot()

    player_app_df = bot.fetch_week_players_statistics(stats_year, stats_season, stats_week, week_note=note)

    bot.teardown_driver()

    return player_app_df
