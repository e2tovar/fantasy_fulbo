from services.scraping_bot import ScrapingBot


def scrap_app_last_week_data(note=''):

    bot = ScrapingBot()

    player_app_df = bot.fetch_last_week_players_statistics(week_note=note)

    bot.teardown_driver()

    return player_app_df