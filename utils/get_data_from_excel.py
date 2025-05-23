import pandas as pd
from utils.streamlit_notifications import autogol_dialog

def read_excel_teams_results(file_path):
    # Lee team resultados. Tabla 1
    # -----------------------------------------------------------------------------------------------------------------
    try:
        df_resultado = pd.read_excel(file_path, sheet_name='Partido', skiprows=3, usecols='B:G')
    except FileNotFoundError:
        print(f"Error al leer el archivo de la jornada {file_path}. Asegurate de que lo has subido correctamente")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    df_resultado.columns = ['local', 'vs', 'away', 'local_goals', '-', 'away_goals']
    df_resultado = df_resultado.drop(['vs', '-'], axis=1)
    df_resultado.dropna(inplace=True)
    # add game_number
    df_resultado['game_number'] = df_resultado.index + 1

    # to int
    df_resultado['local_goals'] = pd.to_numeric(df_resultado['local_goals'], errors='coerce').fillna(0).astype(int)
    df_resultado['away_goals'] = pd.to_numeric(df_resultado['away_goals'], errors='coerce').fillna(0).astype(int)

    # Obtenemos team stats matemáticamente por los resultados
    # -----------------------------------------------------------------------------------------------------------------
    df_stats = df_resultado.copy()
    teams = df_stats['local'].unique()
    # add columns
    for team in teams:
        df_stats[team] = 0

    df_stats['own_goal'] = 0

    # ganados, perdidos, empatados
    df_stats['local_wins'] = df_stats.apply(lambda x: 1 if x['local_goals'] > x['away_goals'] else 0, axis=1)
    df_stats['local_defeats'] = df_stats.apply(lambda x: 1 if x['away_goals'] > x['local_goals'] else 0, axis=1)
    df_stats['local_draws'] = df_stats.apply(lambda x: 1 if x['local_goals'] == x['away_goals'] else 0, axis=1)
    df_stats['away_wins'] = df_stats.apply(lambda x: 1 if x['away_goals'] > x['local_goals'] else 0, axis=1)
    df_stats['away_defeats'] = df_stats.apply(lambda x: 1 if x['local_goals'] > x['away_goals'] else 0, axis=1)
    df_stats['away_draws'] = df_stats.apply(lambda x: 1 if x['local_goals'] == x['away_goals'] else 0, axis=1)


    # puntos
    df_stats['local_points'] = df_stats.apply(
        lambda x: 3 if x['local_goals'] > x['away_goals']
        else 1 if x['local_goals'] == x['away_goals'] else 0, axis=1)
    df_stats['away_points'] = df_stats.apply(
        lambda x: 3 if x['away_goals'] > x['local_goals']
        else 1 if x['away_goals'] == x['local_goals'] else 0, axis=1)

    # Rename
    local_stats = df_stats[[
        'local', 'local_goals', 'away_goals', 'local_points', 'local_wins', 'local_defeats', 'local_draws', 'own_goal']].rename(
        columns={
            'local': 'team', 'local_goals': 'goals', 'away_goals': 'goals_against', 'local_points': 'points',
            'local_wins': 'wins', 'local_defeats': 'defeats', 'local_draws': 'draws'})
    away_stats = df_stats[[
        'away', 'away_goals', 'local_goals', 'away_points', 'away_wins', 'away_defeats', 'away_draws', 'own_goal']].rename(
        columns={
            'away': 'team', 'away_goals': 'goals', 'local_goals': 'goals_against', 'away_points': 'points',
            'away_wins': 'wins', 'away_defeats': 'defeats', 'away_draws': 'draws'})

    df_stats = pd.concat([local_stats, away_stats])
    df_stats = df_stats.groupby('team').sum().reset_index()

    # Resolve Positions
    df_stats = _resolve_ties(df_stats)

    return df_resultado, df_stats


def read_excel_players_stats(file_path, dict_names_own_goal):
    # Lee tabla de players stats. Tabla 3
    # -----------------------------------------------------------------------------------------------------------------
    df_names = _read_excel_names(file_path)

    try:
        df_player_stats = pd.read_excel(file_path, skiprows=3, sheet_name='Partido', usecols="L:O")
    except Exception as e:
        raise (f"An error occurred while reading the player stats: {e}")

    df_player_stats.columns = ['name', 'team', 'goals', 'assists']
    df_player_stats.dropna(how='all', inplace=True, subset=['goals', 'assists'])
    # Drop values starting by Autogol
    df_player_stats = df_player_stats[~df_player_stats['name'].str.startswith('Autogol')].copy()

    df_stats = df_player_stats.merge(df_names, on=['name', 'team'], how='outer').copy()
    df_stats.fillna(0, inplace=True)


    # Add own goals
    df_stats['own_goals'] = df_stats['name'].map(dict_names_own_goal)
    df_stats['own_goals'] = df_stats['own_goals'].fillna(0)


    # to int
    df_stats['goals'] = df_stats['goals'].astype(int)
    df_stats['assists'] = df_stats['assists'].astype(int)
    df_stats['own_goals'] = df_stats['own_goals'].astype(int)

    return df_stats


def check_excel_players_names(file, db_excel_names):
    df_names = _read_excel_names(file)
    excel_names = df_names['name'].unique()

    # get not matching list
    mismatched_names = [name for name in excel_names if name not in db_excel_names]

    return mismatched_names

def _read_excel_names(file_path):
    try:
        df_names = pd.read_excel(file_path, sheet_name='Lista', skiprows=1)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the Excel file: {e}")
        return None

    df_names.drop(columns=['Orden'], inplace=True)
    df_names.columns = ['name', 'team']
    # Eliminate every row name starting by 'Autogol'
    df_names = df_names[~df_names['name'].str.startswith('Autogol')].copy()

    return df_names

def _resolve_ties(df_stats):
    # Calculate goal difference
    df_stats['goal_difference'] = df_stats['goals'] - df_stats['goals_against']

    # Sort by points, goal difference, and goals for
    df_stats.sort_values(by=['points', 'goal_difference', 'goals'], ascending=[False, False, False], inplace=True)

    # Handle ties
    for i in range(len(df_stats) - 1):
        if df_stats.iloc[i]['points'] == df_stats.iloc[i + 1]['points']:
            if df_stats.iloc[i]['goal_difference'] == df_stats.iloc[i + 1]['goal_difference']:
                if df_stats.iloc[i]['goals'] == df_stats.iloc[i + 1]['goals']:
                    print(f"Tie between teams {df_stats.iloc[i]['team']} and {df_stats.iloc[i + 1]['team']}.")
                    decision = input("Enter 1 if the first team should be ranked higher, otherwise enter 2: ")
                    if decision == '1':
                        df_stats.iloc[i], df_stats.iloc[i + 1] = df_stats.iloc[i + 1], df_stats.iloc[i]

    # Assign positions
    df_stats['position'] = range(1, len(df_stats) + 1)

    # Delete temporary columns
    df_stats.drop(['goal_difference'], axis=1, inplace=True)

    return df_stats
