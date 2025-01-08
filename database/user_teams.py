from .database import execute_query, fetch_query


def add_player_to_team(season, week, user_id, player_id, is_captain=False):
    query = """
        INSERT INTO team (season, week, user_id, player_id, is_captain)
        VALUES (?, ?, ?, ?, ?)"""

    execute_query(query, (season, week, user_id, player_id, is_captain))


def get_team(user_id):
    query = """
        SELECT players.name, players.position, players.price, team.is_captain
        FROM team
        JOIN players ON team.player_id = players.id
        WHERE team.user_id = ?"""
    return fetch_query(query, (user_id,))
