from database.team_results import TeamResultsManager


def init_team_results():
    # Se crea tabla de jugadores
    trm = TeamResultsManager()
    #trm.delete_table()
    #trm.create_table()
    trm.delete_season_results('2024', '1')

if __name__ == "__main__":
    init_team_results()