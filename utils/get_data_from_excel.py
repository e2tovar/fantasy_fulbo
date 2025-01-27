import pandas as pd


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

    # Obtenemos team stats de la tabla de resultados. Tabla 2
    # -----------------------------------------------------------------------------------------------------------------
    df_stats = df_resultado.copy()
    teams = df_stats['local'].unique()
    # add columns
    for team in teams:
        df_stats[team] = 0

    df_stats['own_goal'] = 0

    df_stats['local_points'] = df_stats.apply(
        lambda x: 3 if x['local_goals'] > x['away_goals']
        else 1 if x['local_goals'] == x['away_goals'] else 0, axis=1)
    df_stats['away_points'] = df_stats.apply(
        lambda x: 3 if x['away_goals'] > x['local_goals']
        else 1 if x['away_goals'] == x['local_goals'] else 0, axis=1)

    # Rename
    local_stats = df_stats[['local', 'local_goals', 'away_goals', 'local_points']].rename(
        columns={'local': 'team', 'local_goals': 'goals', 'away_goals': 'goals_against', 'local_points': 'points'})
    away_stats = df_stats[['away', 'away_goals', 'local_goals', 'away_points']].rename(
        columns={'away': 'team', 'away_goals': 'goals', 'local_goals': 'goals_against', 'away_points': 'points'})

    df_stats = pd.concat([local_stats, away_stats])
    df_stats = df_stats.groupby('team').sum().reset_index()

    # get posicion
    df_stats['position'] = df_stats['points'].rank(method='min', ascending=False).astype(int)

    return df_resultado, df_stats


def read_excel_players_stats(file_path):
    # Lee tabla de players stats. Tabla 3
    # -----------------------------------------------------------------------------------------------------------------
    # Primero recopilamos todos los nombres desde la hoja 'Lista'
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

    try:
        df_player_stats = pd.read_excel(file_path, skiprows=3, sheet_name='Partido', usecols="L:O")
    except Exception as e:
        print(f"An error occurred while reading the player stats: {e}")
        return None

    df_player_stats.columns = ['name', 'team', 'goals', 'assists']
    df_player_stats.dropna(how='all', inplace=True, subset=['goals', 'assists'])

    df_stats = df_player_stats.merge(df_names, on=['name', 'team'], how='outer').copy()

    # Maneja autogoles. Localiza palabra Autogol en la columna 'name'
    autogol_indices = df_stats[df_stats['name'].str.startswith('Autogol')].index
    for index in autogol_indices:
        print(f"Parece que hay un Autogol: {df_stats.loc[index, 'name']}")
        print("Selecciona el autor de este autogol: ")
        print(df_names)
        index_name = input("Selecciona un número de los anteriores")
        name = df_names.loc[int(index_name), 'name']
        df_stats.loc[df_stats['name'] == name, 'own_goals'] = df_stats.loc[index, 'goals']
    else:
        df_stats['own_goals'] = 0

    df_stats.drop(autogol_indices, inplace=True)
    df_stats.fillna(0, inplace=True)

    # to int
    df_stats['goals'] = df_stats['goals'].astype(int)
    df_stats['assists'] = df_stats['assists'].astype(int)
    df_stats['own_goals'] = df_stats['own_goals'].astype(int)

    return df_stats
