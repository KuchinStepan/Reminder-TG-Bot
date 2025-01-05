import sqlite3

from common.user import User


def create_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id integer PRIMARY KEY, username text, night integer,
                 morning integer, minutes_offset integer, enabled integer)''')
    conn.commit()
    conn.close()


def add_user_to_db(user: User):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
              (user.user_id, user.username, user.night, user.morning, user.minutes_offset, user.enabled))
    conn.commit()
    conn.close()


def update_user_in_db(user: User):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET username=?, night=?, morning=?, minutes_offset=?, enabled=? WHERE user_id=?",
              (user.username, user.night, user.morning, user.minutes_offset, user.enabled, user.user_id))
    conn.commit()
    conn.close()


def delete_user_from_db(user_id: int):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


def get_users_from_db() -> dict[int, User]:
    users: dict[int, User] = dict()
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    for row in rows:
        user = User(row[0], row[1], row[2], row[3], row[4], row[5])
        users[row[0]] = user
    conn.close()
    return users


def get_users_info(enabled=1):
    result = []
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(f"SELECT username, minutes_offset FROM users WHERE enabled = {enabled}")
    rows = c.fetchall()
    for row in rows:
        result.append('@{:<30} {} мин'.format(row[0], row[1]))
    return '\n'.join(result)
