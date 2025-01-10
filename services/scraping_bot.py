import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

        df = pd.DataFrame(data, columns=['media', 'my_note', 'p', 'goles', 'asistencias', 'rojas', 'amarillas', 'pts', 't'])
        df['nombre'] = names
        df['mvp'] = 0
        df['votes'] = 0
        df['total_votes'] = total_votes
        df.loc[df['nombre'] == star_name, 'mvp'] = 1
        df.loc[df['nombre'] == star_name, 'votes'] = int(votes)

        df = df[df['goles'] != '-'].copy()

        if int(year) == 2024 and int(season) in [1, 2]:
            df['pts'] = df['asistencias']
            df['asistencias'] = 0

        if season == 0:
            df['position'] = None
            df['team'] = None
        else:
            df['position'] = df['pts'].astype(int).rank(ascending=False, method='dense')
            df['team'] = None  # Son agregados desde el excel

        if random_teams:
            colors = {1: 'Amarillo', 2: 'Azul', 3: 'Rojo', 4: 'Negro'}
            df['team'] = df['position'].astype(int).map(colors)

        df['note'] = week_note
        column_mapping = {
            'nombre': 'name',
            'goles': 'goals',
            'asistencias': 'assists',
            'media': 'media',
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

        # drop p t
        df.drop(columns=['p', 't'], inplace=True)

        return df

    def __week_element_selection(self, week):
        weeks = self.driver.find_elements(By.CLASS_NAME, settings.CALENDAR_WEEK_CLASS)

        if not weeks:
            raise Exception("No weeks found in the calendar")

        if week != 0:
            if week >= len(weeks):
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

        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(week_href)

        return self.__scrape_week_data(year, season, week_ind, week_date, week_note=week_note)

    def fetch_last_week_players_statistics(self, week_note=''):
        """
        Retrieves player statistics from the application.
        """
        url = "https://app.sporteasy.net/es/login/?next=https://app.sporteasy.net/es/profile/home/"

        self.setup_driver()
        self.login(url)

        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, settings.DASHBOARD_CLASS)))

        self.driver.get("https://liga-profesional-de-aficionados-al-futbol.sporteasy.net/calendar/list/")
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, settings.season_LIST_BTN_CLASS)))
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, settings.YEAR_SEASON_NAME_CLASS)))

        year_season = self.driver.find_element(By.CLASS_NAME, settings.YEAR_SEASON_NAME_CLASS).text
        year = year_season.split(" ")[1]
        bimester = re.findall(r'\d+', year_season.split(" ")[3])[0]

        print(f"Descargando stats de año {year} - bimestre {bimester}")
        return self.__download_calendar(year, bimester, week_note=week_note)
