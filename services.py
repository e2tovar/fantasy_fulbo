from typing import Dict
import pandas as pd
from rapidfuzz import process

from config.settings import JORNADA_PATH
from utils.procesa_nombres import pre_procesa_nombres


def load_week_from_excel(file_path, match_week, season, player_mapping: Dict):
    """
    Carga los datos de la jornada. Esta es una función crucial
    """

    df_players= pd.read_excel(file_path, sheet_name='Registro', skiprows=1)

    df_resultado = pd.read_excel(file_path, skiprows=18, sheet_name='Partido', usecols="B:J")


    week_data = []
    for _, row in df.iterrows():
        week_data.append((
            row['playersID'],  # Foreign key
            season,
            match_week,
            row['Goals'],
            row['Assists'],
            row['Clean Sheets'],
            row['Team Position']
        ))

    # Step 5: Insert data into the week table
    query = """
        INSERT INTO week (player_id, season, match_week, goals, assists, clean_sheets, team_position)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    for record in week_data:
        execute_query(query, record)

    print(f"Match week {match_week} for season {season} loaded successfully.")


def load_round_player(all_player: pd.DataFrame):
    excel_file = JORNADA_PATH
    round_players= pd.read_excel(excel_file, skiprows=1, sheet_name='Registro')


def update_stats_by_round():
    # Read the last round excel and update stats
    excel_file = JORNADA_PATH
    pd.read_excel(excel_file, index_col=1, skiprows=18, sheet_name='Partido')


def calcular_ranking(jugadores):
    return sorted(jugadores, key=lambda x: x.puntos, reverse=True)
