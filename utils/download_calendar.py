from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from bs4 import BeautifulSoup
import time

from config import settings as st
from utils.save_week import save_week_from_df


def download_calendar(driver: webdriver.Chrome, wait: WebDriverWait, year: int, season: int):
    # get table
    # Wait for the table to be present
    wait.until(EC.presence_of_element_located((By.ID, st.CALENDAR_TABLE_ID)))

    # Select all weeks
    weeks = driver.find_elements(By.CLASS_NAME, st.CALENDAR_WEEK_CLASS)

    # Itera weeks y abre nueva ventana para descargar datos
    for week_ind, week in enumerate(weeks):
        # get href from week if exists, else continue
        if not week.get_attribute('href'):
            continue

        href = week.get_attribute('href')
        # Date is in the next child
        week_date = week.find_element(By.XPATH, "./*").text.split()[0]
        if week_date == '12/10/2024':
            continue
        print(f"Descargando datos de la jornada {week_ind} -- {week_date}")
        # Open new tab
        driver.execute_script("window.open('');")
        # Switch to the new window
        driver.switch_to.window(driver.window_handles[1])
        # Open the week page
        driver.get(href)

        scrape_week_data(driver, wait, year, season, week_ind, week_date)
        # Close the tab
        driver.close()
        # Switch back to the first tab
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(2)


def scrape_week_data(driver, wait, year, season, week, week_date):
    time.sleep(2)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, st.TABLE_CLASS)))
    tables = driver.find_elements(By.CLASS_NAME, st.TABLE_CLASS)
    name_table = tables[0]
    html_content = name_table.get_attribute('outerHTML')
    # BS
    soup = BeautifulSoup(html_content, 'html.parser')

    # Seleccionamos filas de tabla nombre
    name_rows = soup.select(st.NAME_ROWS_CLASS_SOUP)
    # Extraemos Datos (nombres)
    names = []
    data = []
    for row in name_rows:
        name = row.select_one(st.NAME_TEXT_CLASS_SOUP).text
        names.append(name)

    # Stats
    # ----------------------------------------------------------
    stats_table = tables[1]
    html_content = stats_table.get_attribute('outerHTML')
    # BS
    soup = BeautifulSoup(html_content, 'html.parser')

    # seleccionamos filas de la tabla stats
    stats_rows = soup.select(st.STATS_ROWS_CLASS_SOUP)
    # Extraemos Datos (stats)
    for row in stats_rows:
        columns = row.select(st.STATS_VALUE_CLASS_SOUP)  # Selector para las celdas
        values = [col.text.strip() for col in columns]
        data.append(values)

    # Extraer estrella del partido
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, st.STAR_NAME_CLASS)))
    star_name = driver.find_element(By.CLASS_NAME, st.STAR_NAME_CLASS).text.strip()
    star_votes = driver.find_element(By.CLASS_NAME, st.STAR_VOTE_CLASS).text
    votes = star_votes.replace('Votos', '').split('/')[0].strip()
    total_votes = star_votes.replace('Votos', '').split('/')[1].strip()

    # Convertir los datos a un DataFrame para un manejo más cómodo
    df = pd.DataFrame(data, columns=['media', 'my_note', 'p', 'goles', 'asistencias', 'rojas', 'amarillas', 'pts', 't'])
    df['nombre'] = names
    df['mvp'] = 0
    df['votes'] = 0
    df['total_votes'] = total_votes
    df.loc[df['nombre'] == star_name, 'mvp'] = 1
    df.loc[df['nombre'] == star_name, 'votes'] = int(votes)

    # quitamos a los que no participan (goles = '-')
    df = df[df['goles'] != '-'].copy()

    # En jornada 1 y 2 no se contaban asistencias y se anotaba el resultado ahí (rank)
    if int(year) == 2024 and int(season) in [1, 2]:
        df['pts'] = df['asistencias']
        df['asistencias'] = 0

    if season == 0:
        df['rank'] = None
        df['team'] = None
    else:
        df['rank'] = df['pts'].astype(int).rank(ascending=False, method='dense')
        # team en dependencia del rank. Asignamos un color por cada rank
        colors = {
            1: 'Amarillo',
            2: 'Azul',
            3: 'Rojo',
            4: 'Negro'
            }
        df['team'] = df['rank'].astype(int).map(colors)

    # Nota
    df['note'] = """
        Datos desde app, 2023 faltan muchos datos.
        Faltan pts y goles de equipos en tabla team_results
        Los colores de los equipos no son los reales
        No se anotaba el rking de equipos
        """

    df = df[[
        'nombre', 'goles', 'asistencias', 'media', 'mvp', 'amarillas',
        'rojas', 'votes', 'total_votes', 'team', 'rank', 'note']].copy()
    df.columns = [
        'name', 'goals', 'assists', 'media', 'mvp', 'yellow_card', 'red_card',
        'votes', 'total_votes', 'team', 'rank', 'note']

    df['year'] = year
    df['seasson'] = season
    df['match_week'] = week
    df['week_date'] = week_date

    # Guardar datos en la base de datos
    save_week_from_df(df)
