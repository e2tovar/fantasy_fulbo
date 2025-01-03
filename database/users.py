from .database import execute_query, fetch_query


class UserManager:

    def create_table(self):
        execute_query("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                budget REAL NOT NULL,
                total_points INTEGER DEFAULT 0
            )
        """)

    def get_user(self, user_id):
        for user in self.users:
            if user[0] == user_id:
                return user
        return None

def add_user(name, budget=77.0):
    query = "INSERT INTO users (name, budget) VALUES (?, ?)"
    execute_query(query, (name, budget))


def get_users():
    query = "SELECT * FROM users"
    return fetch_query(query)


def update_user_points(user_id, points):
    query = "UPDATE users SET total_points = total_points + ? WHERE id = ?"
    execute_query(query, (points, user_id))


def delete_user(user_id):
    query = "DELETE FROM users WHERE id = ?"
    execute_query(query, (user_id,))
