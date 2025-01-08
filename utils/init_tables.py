from pandas import DataFrame as pd

from database.player_statistics import PlayerStatisticsManager
from database.team_stats import TeamStatsManager
from database.team_results import TeamResultsManager
from database.players import PlayerManager
from config.constatnts import MAPEO_APP_FANTASY


def init_players_statistics():
    # Se crea tabla de jugadores
    weekm = PlayerStatisticsManager()
    weekm.delete_table()
    weekm.create_table()

def init_team_results():
    # Se crea tabla de jugadores
    weekm = TeamResultsManager()
    weekm.delete_table()
    weekm.create_table()

def init_team_stats():
    # Se crea tabla de jugadores
    weekm = TeamStatsManager()
    weekm.delete_table()
    weekm.create_table()


def init_players():
    # Se crea tabla de jugadores
    players = PlayerManager()
    players.delete_table()
    players.create_table()

    # Se cargan los jugadores
    player_df = pd.read_excel("data/fantasy/fantasy.xlsx", sheet_name="Valores de Jugadores")
    player_df = player_df.iloc[:, :-1].copy()

    # invertir mapeo_fantasy
    mapeo = {v: k for k, v in MAPEO_APP_FANTASY.items()}

    player_df.columns = ["name", "position", "price"]
    player_df['name_fantasy'] = player_df['name'].map(mapeo)

    plm = PlayerManager()

    for _, row in player_df.iterrows():
        plm.add_player(row["name"], row['name_fantasy'], row["position"], row["price"])

if __name__ == "__main__":
    #init_players_statistics()
    init_team_results()
    #init_team_stats()
    #init_players()
