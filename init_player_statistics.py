import pandas as pd
import os

from database.player_statistics import PlayerStatisticsManager
from database.players import PlayerManager
from config.constatnts import MAPEO_APP_FANTASY

def init_players_statistics():
    # Se crea tabla de jugadores
    weekm = PlayerStatisticsManager()
    weekm.delete_table()
    weekm.create_table()
