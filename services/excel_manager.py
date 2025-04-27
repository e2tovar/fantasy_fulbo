

import pandas as pd


class ExcelManager:
    def __init__(self):
        self.excel_file = None
        self.df_week_names = None
        self.df_team_result_raw = None
        self.df_player_stats_raw = None

    def read_excel(self, excel_file):
        self.excel_file = excel_file
        self.get_excel_names()
        self.get_excel_team_results()
        self.get_excel_player_stats()

    def get_excel_names(self):
        # Lee los nombres de los jugadores de la sheet Lista
        try:
            df_names = pd.read_excel(self.excel_file, sheet_name='Lista', skiprows=1)
        except FileNotFoundError:
            raise Exception(f"Archivo no encontrado: {self.excel_file}")
        except ValueError as ve:
            raise Exception(f"Error en la hoja 'Lista' del archivo {self.excel_file}: {ve}")
        except Exception as e:
            raise Exception(f"Error inesperado al leer {self.excel_file}: {e}")

        df_names.drop(columns=['Orden'], inplace=True)
        df_names.columns = ['name', 'team']
        # Eliminate every row name starting by 'Autogol'
        df_names = df_names[~df_names['name'].str.startswith('Autogol')].copy()

        self.df_week_names = df_names

    def get_excel_team_results(self):
        # Lee los resultados de la sheet Partido
        try:
            df = pd.read_excel(self.excel_file, sheet_name='Partido', skiprows=3, usecols='B:G')
        except FileNotFoundError:
            raise Exception(f"Archivo no encontrado: {self.excel_file}")
        except ValueError as ve:
            raise Exception(f"Error en la hoja 'Partido' del archivo {self.excel_file}: {ve}")
        except Exception as e:
            raise Exception(f"Error inesperado al leer {self.excel_file}: {e}")

        self.df_team_result_raw = df

    def get_excel_player_stats(self):
        # Lee las estadísticas de la sheet Partido
        try:
            df = pd.read_excel(self.excel_file, skiprows=3, sheet_name='Partido', usecols="L:O")
        except FileNotFoundError:
            raise Exception(f"Archivo no encontrado: {self.excel_file}")
        except ValueError as ve:
            raise Exception(f"Error en la hoja 'Jugadores' del archivo {self.excel_file}: {ve}")
        except Exception as e:
            raise Exception(f"Error inesperado al leer {self.excel_file}: {e}")

        df.columns = ['name', 'team', 'goals', 'assists']
        df.dropna(how='all', inplace=True, subset=['goals', 'assists'])

        self.df_player_stats_raw = df

    def fetch_excel_teams_results(self):
        df_resultado = self.df_team_result_raw.copy()

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
        df_stats = self._resolve_ties(df_stats)

        return df_resultado, df_stats

    def fetch_excel_players_stats(self, dict_names_own_goal):
        # Lee tabla de players stats. Tabla 3
        # -----------------------------------------------------------------------------------------------------------------
        df_names = self.df_week_names.copy()
        df_player_stats = self.df_player_stats_raw.copy()

        df_stats = df_player_stats.merge(df_names, on=['name', 'team'], how='outer').copy()

        if not dict_names_own_goal:
            # Maneja autogoles. Localiza palabra Autogol en la columna 'name'
            autogol_indices = df_stats[df_stats['name'].str.startswith('Autogol')].index

            owng_team_list = []

            for index in autogol_indices:
                number_owg = df_stats.loc[index, 'goals']
                owng_team_list += [df_stats.loc[index, 'name']] * int(number_owg)

            if len(owng_team_list) > 0:
                try:
                    dict_names_own_goal = autogol_dialog(owng_team_list, df_stats)
                except Exception as e:
                    raise f"An error occurred while handling autogols: {e}"

        # Add own goals
        df_stats['own_goals'] = df_stats['name'].map(dict_names_own_goal)
        df_stats['own_goals'] = df_stats['own_goals'].fillna(0)

        # to int
        df_stats['goals'] = df_stats['goals'].astype(int)
        df_stats['assists'] = df_stats['assists'].astype(int)
        df_stats['own_goals'] = df_stats['own_goals'].astype(int)

        return df_stats

    def check_missing_excel_players_names(self, db_excel_names):
        df_names = self.df_week_names.copy()
        excel_names = df_names['name'].unique()

        # get not matching list
        mismatched_names = [name for name in excel_names if name not in db_excel_names]

        return mismatched_names

    def check_teams_own_goals(self):
        df_stats = self.df_player_stats_raw.copy()
        autogol_indices = df_stats[df_stats['name'].str.startswith('Autogol')].index

        owng_team_list = []

        for index in autogol_indices:
            number_owg = df_stats.loc[index, 'goals']
            owng_team_list += [df_stats.loc[index, 'name']] * int(number_owg)

        return owng_team_list


    @staticmethod
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
