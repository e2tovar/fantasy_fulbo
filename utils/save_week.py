import pandas as pd
import rapidfuzz.process as rfuzz

from database.player_statistics import PlayerStatisticsManager
from database.players import PlayerManager
from database.team_results import TeamResultsManager


def save_week_from_df(df: pd.DataFrame):
    # obtenemos player_id
    pm = PlayerManager()
    player_ids = pm.get_fantasyname_id_dict()
    df['id'] = df['name'].map(player_ids)

    # Si existe un jugador con id null es un nuevo jugador, preguntaremos si se quiere insertar en tabla players
    if df['id'].isnull().any():
        print("Se han encontrado jugadores no registrados en la base de datos")
        new_players = df[df['id'].isnull()]['name'].unique()
        for player in new_players:
            # Obten similares sugeridos
            players = pm.get_all_players()
            names = players['name_fantasy'].values

            names_id = players.reset_index()[['name_fantasy', 'id']].set_index('name_fantasy').to_dict()['id']
            matchs = rfuzz.extract(player.lower().replace('invitado', ''), names, score_cutoff=50)
            sugested_players = [match[0] for match in matchs]
            sugested_names_ids = {name: names_id[name] for name in sugested_players}
            print('---------------------------------------------------------')
            print(f" '{player}' podría tratarse de un jugador existente: ")
            print(f"{sugested_names_ids})", end='\n')

            print(f"¿Qué hacer con {player}. Seleccione una opción(número)")
            print("1: Agregar nuevo jugador")
            print("2: Asignar a un jugador ya existente")
            response = input()
            if response == '1':
                price = 10
                print("Ingrese la posición del jugador: ")
                print("1: Delantero")
                print("2: Mediocampista")
                print("3: Defensor")
                position = input()
                if position == '1':
                    position = 'Delantero'
                elif position == '2':
                    position = 'Mediocampista'
                elif position == '3':
                    position = 'Defensor'
                player_id = pm.add_player(player, player, position, price)
                df.loc[df['name'] == player, 'id'] = player_id
            elif response == '2':
                # obtener mejor match
                print("Ingrese el id drl jugador: ")
                player_id = input()
                df.loc[df['name'] == player, 'id'] = player_id

    # Guardar datos
    # Stats
    for _, row in df.iterrows():
        # Stats
        psm = PlayerStatisticsManager()
        psm.add_player_statistics(
            player_id=row['id'],
            year=row['year'],
            seasson=row['seasson'],
            match_week=row['match_week'],
            team=row['team'],
            date=row['week_date'],
            goals=row['goals'],
            assists=row['assists'],
            media=row['media'],
            mvp=row['mvp'],
            yellow_card=row['yellow_card'],
            red_card=row['red_card'],
            votes=row['votes'],
            total_votes=row['total_votes'],
            note=row['note']
        )

    # Team
    if df['rank'].isnull().all():
        return
    trm = TeamResultsManager()
    # group by team, year(last), seasson(last), match_week(last), goals(sum), rank(last)
    df['goals'] = df['goals'].astype(int)
    df = df.sort_values(by='rank')
    df_team = df.groupby('team').agg({
        'year': 'last', 'seasson': 'last', 'match_week': 'last', 'goals': 'sum', 'rank': 'last'}).reset_index().copy()

    for _, row in df_team.iterrows():
        trm.add_team_result(
            year=row['year'],
            season=row['seasson'],
            match_week=row['match_week'],
            team_name=row['team'],
            goals=row['goals'],
            goals_against=None,
            points=None,
            rank=row['rank']
        )
