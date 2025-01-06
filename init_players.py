import pandas as pd
from database.players import PlayerManager
from config.constatnts import MAPEO_APP_FANTASY


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
