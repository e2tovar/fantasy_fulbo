from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time
import re

from config import settings
from utils.download_calendar import download_calendar
from init_player_statistics import init_players_statistics
from init_team_stats import init_team_stats


# Request users and pass
users = "e2varadero@gmail.com"
password = "Fantasy2025!"
url = "https://app.sporteasy.net/es/login/?next=https://app.sporteasy.net/es/profile/home/"


# init table. OJO esto borra la tabla
# init_players_statistics()
# init_team_stats()

# Abrir navegador
season_options = webdriver.ChromeOptions()

# Set options
season_options.add_argument("--start-maximized")
if settings.HEADLESS:
    season_options.add_argument("--headless")

driver = webdriver.Chrome(options=season_options)
wait = WebDriverWait(driver, timeout=60)

# abrir url
driver.get(url)

# Ingresar usuario
wait.until(EC.presence_of_element_located((By.NAME, "username")))
user_box = driver.find_element(By.NAME, "username")
user_box.send_keys(users)

# Ingresar contraseña
password_box = driver.find_element(By.NAME, "password")
password_box.send_keys(password)

# Click en el botón de login
submit_bt = driver.find_element(By.ID, "SubmitButton")
submit_bt.click()
time.sleep(2)

# Abrimos calendario
driver.get("https://liga-profesional-de-aficionados-al-futbol.sporteasy.net/calendar/list/")
# clikeamos los settings
# Esperar a que carge la página
wait.until(EC.presence_of_element_located((By.CLASS_NAME, settings.season_LIST_BTN_CLASS)))
# click en el boton de settings
driver.find_element(By.CLASS_NAME, settings.season_LIST_BTN_CLASS).click()

season_options = driver.find_elements(By.CLASS_NAME, "select__option")


for i in range(len(season_options)):
    if i > 0:
        driver.find_element(By.CLASS_NAME, settings.season_LIST_BTN_CLASS).click()

    season_options = driver.find_elements(By.CLASS_NAME, "select__option")
    # force last season
    season = season_options[i]
    season.click()

    # Recuperamos datos de temporada
    if i == len(season_options) - 1:  # Caso para 2023
        year = 2023
        bimester = 0
    else:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, settings.YEAR_SEASON_NAME_CLASS)))
        year_season = driver.find_element(By.CLASS_NAME, settings.YEAR_SEASON_NAME_CLASS).text
        # Ej: Temporada 2024 - 6to Bimestre. Bimestre en int
        year = year_season.split(" ")[1]
        bimester = year_season.split(" ")[3]
        # extrae numero de bimestre
        bimester = re.findall(r'\d+', bimester)[0]

    # forzar season
    if not (int(year) == 2024 and int(bimester) == 1):
        continue

    print(f"Descargando stats de año {year} - bimestre {bimester}")

    download_calendar(driver, wait, year, bimester)
