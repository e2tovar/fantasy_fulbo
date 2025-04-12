import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from typing import List


from config import settings

load_dotenv()

class ScrapingBot:
    def __init__(self, headless=settings.HEADLESS):
        """
        Initializes a ScrapingBot instance.

        Parameters:
        headless (bool): Determines if the browser should run in headless mode. Defaults to True.
        week (int): Specifies the week number for data scraping. Defaults to 0.

        Attributes:
        headless (bool): Stores the headless mode setting.
        driver (webdriver.Chrome): The Selenium WebDriver instance, initialized in setup_driver.
        wait (WebDriverWait): The WebDriverWait instance for managing waits, initialized in setup_driver.
        """
        self.headless = headless
        self.driver = None
        self.wait = None

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        if self.headless:
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, timeout=60)

    def teardown_driver(self):
        if self.driver:
            self.driver.quit()

    def login(self, url):
        """
        Logs into the target website using credentials from environment variables.

        Parameters:
        url (str): The URL of the login page.
        """
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        user_box = self.driver.find_element(By.NAME, "username")
        user_box.send_keys(os.getenv("APP_USERNAME"))

        password_box = self.driver.find_element(By.NAME, "password")
        password_box.send_keys(os.getenv("APP_PASSWORD"))

        submit_bt = self.driver.find_element(By.ID, "SubmitButton")
        submit_bt.click()

    @staticmethod
    def _pick_year_season(options: List[WebElement], pick_year, pick_season) -> WebElement:
        # Option str = [x]er Bimestre - [y] where x=season and y=year
        for option in options:
            text = option.text
            year_text = text.split('-')[0].strip()
            season_text = text.split('-')[1].strip()
            if str(pick_year) in year_text and str(pick_season) in season_text:
                return option

        raise ValueError(f"No se encontró la temporada {pick_season} {pick_year}")

    def _extract_names(self, table_element):
        html_content = table_element.get_attribute('outerHTML')
        soup = BeautifulSoup(html_content, 'html.parser')
        name_rows = soup.select(settings.NAME_ROWS_CLASS_SOUP)
        return [row.select_one(settings.NAME_TEXT_CLASS_SOUP).text for row in name_rows]

    def _extract_stats(self, table_element):
        html_content = table_element.get_attribute('outerHTML')
        soup = BeautifulSoup(html_content, 'html.parser')
        stats_rows = soup.select(settings.STATS_ROWS_CLASS_SOUP)
        return [[col.text.strip() for col in row.select(settings.STATS_VALUE_CLASS_SOUP)] for row in stats_rows]

    def __scrape_week_data(self, year, season, week, week_date, week_note='', random_teams=False):
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, settings.TABLE_CLASS)))

        # Re-fetch the tables to ensure they are fully loaded
        tables = self.driver.find_elements(By.CLASS_NAME, settings.TABLE_CLASS)

        # Wait for the expected number of column in the second table
        self.wait.until(lambda _: len(tables[1].find_element(
            By.CLASS_NAME, "RYFw3QcNNvVNj3bsW8gM").find_elements(By.XPATH, "./*")) == 9)

        names = self._extract_names(tables[0])
        data = self._extract_stats(tables[1])

        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, settings.STAR_NAME_CLASS)))
        star_name = self.driver.find_element(By.CLASS_NAME, settings.STAR_NAME_CLASS).text.strip()
        star_votes = self.driver.find_element(By.CLASS_NAME, settings.STAR_VOTE_CLASS).text
        votes, total_votes = map(str.strip, star_votes.replace('Votos', '').split('/'))

        df = pd.DataFrame(data, columns=['my_note', 'p', 'goles', 'asistencias', 'rojas', 'amarillas', 'pts', 't'])
        df['nombre'] = names
        df['mvp'] = 0
        df['votes'] = 0
        df['total_votes'] = total_votes
        df.loc[df['nombre'] == star_name, 'mvp'] = 1
        df.loc[df['nombre'] == star_name, 'votes'] = int(votes)

        df = df[df['goles'] != '-'].copy()

        column_mapping = {
            'nombre': 'name',
            'goles': 'goals',
            'asistencias': 'assists',
            'mvp': 'mvp',
            'amarillas': 'yellow_card',
            'rojas': 'red_card',
            'votes': 'votes',
            'total_votes': 'total_votes',
            'team': 'team',
            'position': 'position',
            'note': 'note'
        }
        df = df.rename(columns=column_mapping)

        df['year'] = year
        df['season'] = season
        df['match_week'] = week
        df['date'] = week_date

        # Tomamos los equipos desde el excel
        df['yellow_card'] = 0
        df['red_card'] = 0

        # drop p t
        df.drop(columns=['p', 't', 'goals', 'assists', 'pts'], inplace=True)

        return df

    def __week_element_selection(self, week):
        weeks = self.driver.find_elements(By.CLASS_NAME, settings.CALENDAR_WEEK_CLASS)

        if not weeks:
            raise Exception("No weeks found in the calendar")

        week = int(week)

        if week != 0:
            if int(week) >= len(weeks):
                raise IndexError("Specified week is out of range.")
            week_e = weeks[week]
            week_ind = week
            week_ele = week_e
        else:  # last week
            weeks = weeks[::-1]
            ntries = 0
            for week_e in weeks:
                text_font_color = week_e.find_element(By.XPATH, "./*").value_of_css_property('color')
                if text_font_color == 'rgba(132, 138, 144, 1)':
                    week_ind = len(weeks) - 1 - ntries
                    week_ele = week_e
                    break
                ntries += 1
            else:
                raise Exception("No hay jornada disponible")

        href = week_ele.get_attribute('href')
        week_date = week_ele.find_element(By.XPATH, "./*").text.split()[0]
        return week_ind, week_date, href

    def __download_calendar(self, year, season, week=0, week_note=''):
        self.wait.until(EC.presence_of_element_located((By.ID, settings.CALENDAR_TABLE_ID)))
        week_ind, week_date, week_href = self.__week_element_selection(week)

        print(f"Descargando stats de año {year} - bimestre {season} - jornada {week_ind}")

        self.driver.get(week_href)

        return self.__scrape_week_data(year, season, week_ind, week_date, week_note=week_note)

    def fetch_week_players_statistics(self, stats_year, stats_season, stats_week, week_note=''):
        """
        Retrieves player statistics from the application.
        """
        url = "https://app.sporteasy.net/es/login/?next=https://app.sporteasy.net/es/profile/home/"

        # Home
        self.setup_driver()
        self.login(url)

        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, settings.DASHBOARD_CLASS)))

        # Calendar
        self.driver.get("https://liga-profesional-de-aficionados-al-futbol.sporteasy.net/calendar/list/")
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, settings.SEASSON_LIST_BTN_CLASS)))
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, settings.YEAR_SEASON_NAME_CLASS)))

        # Click years_season list
        self.driver.find_element(By.CLASS_NAME, settings.SEASSON_LIST_BTN_CLASS).click()
        # Options
        season_options = self.driver.find_elements(By.CLASS_NAME, settings.YEAR_SEASON_OPTIONS_CLASS)
        # Select year-season
        self._pick_year_season(season_options, stats_year, stats_season).click()

        return self.__download_calendar(stats_year, stats_season, stats_week, week_note=week_note)
