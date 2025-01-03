import pandas as pd
import os

from database.player_statistics import PlayerStatisticsManager
from database.players import PlayerManager
from config.constatnts import MAPEO_APP_FANTASY

# Se crea tabla de jugadores
weekm = PlayerStatisticsManager()
weekm.delete_table()
weekm.create_table()


'''
plm = PlayerManager()
db_names_id_map = plm.get_player_mapping()


sin_map = []

# Se cargan todos los excels de la carpeta jornadas
for file in os.listdir("data/jornadas"):
    if file.endswith(".xlsx"):
        week_df = pd.read_excel("data/jornadas/" + file)
        week_df = week_df.iloc[:, 1:].copy()
        file = file.replace(".xlsx", "")
        year = file.split("_")[0]
        seasson = file.split("_")[1]
        week = file.split("_")[2]

        week_df['nombre_fantasy'] = week_df['nombre'].map(MAPEO_APP_FANTASY)
        sin_map.append(week_df[week_df['nombre_fantasy'].isna()]['nombre'].tolist())

        week_df.dropna(subset=['nombre_fantasy'], inplace=True)

        excel_names = week_df["nombre"].tolist()

        # Reemplazo los nombres por los ids
        week_df["id"] = week_df["nombre_fantasy"].map(db_names_id_map)
        week_df = week_df.drop(columns=["nombre", "nombre_fantasy"])

        for index, row in week_df.iterrows():
            weekm.add_week(
                player_id=row["id"],
                year=year,
                seasson=seasson,
                match_week=week,
                goals=row["goles"],
                assists=row["asistencias"],
                clean_sheets=None,
                mvp=row["mvp"],
                media=row["media"],
                yellow_card=row['amarillas'],
                red_card=row['rojas']
            )
'''