import pandas as pd


def read_excel_teams_results(file_path):
    # Lee team resultados. Tabla 1
    # -----------------------------------------------------------------------------------------------------------------
    df_resultado = pd.read_excel(file_path, sheet_name='Partido', skiprows=3, usecols='B:G')
    df_resultado.columns = ['local', 'vs', 'away', 'local_goals', '-', 'away_goals']
    df_resultado = df_resultado.drop(['vs', '-'], axis=1)
    df_resultado.dropna(inplace=True)
    # add game_number
    df_resultado['game_number'] = df_resultado.index + 1

    # to int
    df_resultado['local_goals'] = df_resultado['local_goals'].astype(int)
    df_resultado['away_goals'] = df_resultado['away_goals'].astype(int)

    # Obtenemos team stats de la tabla de resultados. Tabla 2
    # -----------------------------------------------------------------------------------------------------------------
    df_stats = df_resultado.copy()
    teams = df_stats['local'].unique()
    # add columns
    for team in teams:
        df_stats[team] = 0

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

    # get rank
    df_stats['rank'] = df_stats['points'].rank(method='min', ascending=False).astype(int)

    return df_resultado, df_stats


def read_excel_players():
    # Lee tabla de players stats. Tabla 3
    # -----------------------------------------------------------------------------------------------------------------
    df_player_stats = pd.read_excel(file_path, skiprows=3, sheet_name='Partido', usecols="L:O")
    df_player_stats.columns = ['name', 'team', 'goals', 'assists']
    df_player_stats.dropna(how='all', inplace=True, subset=['goals', 'assists'])
    df_player_stats.fillna(0, inplace=True)
    # to int
    df_player_stats['goals'] = df_player_stats['goals'].astype(int)
    df_player_stats['assists'] = df_player_stats['assists'].astype(int)

    return df_player_stats
