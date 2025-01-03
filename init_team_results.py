from database.team_results import TeamResultsManager

# Se crea tabla de jugadores
trm = TeamResultsManager()
trm.delete_table()
trm.create_table()
