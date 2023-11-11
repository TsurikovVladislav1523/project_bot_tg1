import sqlite3


def create_db():
    conn = sqlite3.connect('my_database.db')

    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        tg_id TEXT,
                        token TEXT NULL, 
                        secret_key TEXT NULL
                    )''')
    conn.commit()
    conn.close()


def delete_user_by_tg_id(tg_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE tg_id = ?", (tg_id,))

    conn.commit()
    conn.close()


def add_solo_user(tg_id, token):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (tg_id, token, secret_key) VALUES (?, ?, ?)", (tg_id, token, None))

    conn.commit()
    conn.close()


def add_main_family_user(tg_id, token, secret_key):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (tg_id, token, secret_key) VALUES (?, ?, ?)", (tg_id, token, secret_key))

    conn.commit()
    conn.close()


def add_other_family_user(tg_id, secret_key):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (tg_id, token, secret_key) VALUES (?, ?, ?)", (tg_id, None, secret_key))

    conn.commit()
    conn.close()


def get_token_by_tg_id(tg_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT token FROM users WHERE tg_id=?", (tg_id,))
    result = cursor.fetchone()

    if result:
        token = result[0]
        if token is None:
            cursor.execute("SELECT secret_key FROM users WHERE tg_id=?", (tg_id,))
            secret_key = cursor.fetchone()

            cursor.execute("SELECT token FROM users WHERE secret_key=?", (secret_key[0],))
            token = cursor.fetchone()
            conn.close()

            return token[0]
        else:
            conn.close()
            return token
    else:
        conn.close()
        return False

# типо тесты
#
# add_solo_user("1", "solosolosolo")
# print(get_token_by_tg_id("1"))
# print(get_token_by_tg_id("0"))
#
# add_main_family_user("2", "token", "verysecretkey")
# print(get_token_by_tg_id("2"))
# print(get_token_by_tg_id("3"))
#
# add_other_family_user("56", "verysecretkey")
# print(get_token_by_tg_id("56"), "и токен владельца семьи: " + get_token_by_tg_id("2"))
#
# add_other_family_user("78", "notsecretkey")
# print(get_token_by_tg_id("78"))
