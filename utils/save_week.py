from database.team_results import TeamResultsManager
from database.team_stats import TeamStatsManager
from database.player_statistics import PlayerStatisticsManager

import pandas as pd
import rapidfuzz.process as rfuzz





def save_week_players_stats_from_df(df: pd.DataFrame):
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
    if df.isnull().values.any():
        raise ValueError("DataFrame contains missing or null values.")
    for row in df.itertuples(index=False):
        try:
            psm = PlayerStatisticsManager()
            psm.add_player_statistics(
                player_id=row.id,
                year=row.year,
                season=row.season,
                match_week=row.match_week,
                team=row.team,
                date=row.week_date,
                goals=row.goals,
                assists=row.assists,
                media=row.media,
                mvp=row.mvp,
                yellow_card=row.yellow_card,
                red_card=row.red_card,
                votes=row.votes,
                total_votes=row.total_votes,
                note=row.note
            )
        except Exception as e:
            print(f"Error saving statistics for player {row.name} in match week {row.match_week}: {e}")

def save_week_team_result_from_df(df: pd.DataFrame, trm: TeamResultsManager) -> None:
    """
    Save team results from a DataFrame to a TeamResultsManager.

    :param df: DataFrame containing match data.
    :param trm: Instance of TeamResultsManager.
    """
    required_columns = {'game_number', 'year', 'season', 'match_week', 'local', 'away', 'local_goals', 'away_goals'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"DataFrame is missing required columns: {required_columns - set(df.columns)}")

    results = [
        (row['game_number'],
         row['year'],
         row['season'],
         row['match_week'],
         row['local'],
         row['away'],
         row['local_goals'],
         row['away_goals'])
        for _, row in df.iterrows()
    ]
    try:
        trm.add_team_results_week(results)
    except Exception as e:
        print(f"Error saving team results batch: {e}")

def save_week_team_stats_from_df(df: pd.DataFrame, tsm: TeamStatsManager) -> None:
    """
    Save team statistics from a DataFrame to a TeamStatsManager.

    :param df: DataFrame containing team statistics.
    :param tsm: Instance of TeamStatsManager.
    """
    required_columns = {'year', 'season', 'match_week', 'team', 'goals', 'goals_against', 'points', 'rank'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"DataFrame is missing required columns: {required_columns - set(df.columns)}")

    stats = [
        (row['year'], row['season'], row['match_week'], row['team'], row['goals'], row['goals_against'],
         row['points'], row['rank'])
        for _, row in df.iterrows()
    ]
    try:
        tsm.add_team_stats_week(stats)
    except Exception as e:
        print(f"Error saving team stats batch: {e}")
