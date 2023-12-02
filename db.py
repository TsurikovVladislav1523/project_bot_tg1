import sqlite3
from read_pet_lists import read_pet_lists

cats_list, dogs_list = read_pet_lists()


def create_db():
    conn = sqlite3.connect('users.db')

    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        tg_id TEXT,
                        token TEXT NULL, 
                        secret_key TEXT NULL,
                        user_cat TEXT NULL,
                        user_dog TEXT NULL
                    )''')
    conn.commit()
    conn.close()


def delete_user_by_tg_id(tg_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE tg_id = ?", (tg_id,))

    conn.commit()
    conn.close()


def check_tg_id_exists(tg_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE tg_id=?", (tg_id,))

    result = cursor.fetchone()

    conn.close()

    if result:
        return True
    else:
        return False


def get_user_pets(tg_id):
    if check_tg_id_exists(tg_id):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("SELECT user_cat, user_dog FROM users WHERE tg_id=?", (tg_id,))

        result = cursor.fetchone()

        conn.close()

        if result:
            user_cat, user_dog = result
            return user_cat, user_dog
        else:
            return None, None
    else:
        print("Ошибка: пользователя с таким tg_id не существует")
        return None


def add_user_pet(tg_id, user_pet):
    if check_tg_id_exists(tg_id):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        if user_pet in cats_list:
            try:
                cursor.execute("UPDATE users SET user_cat = ? WHERE tg_id = ?", (user_pet, tg_id))
                conn.commit()
                print(f"Данные для tg_id {tg_id} успешно вставлены.")
            except sqlite3.Error as e:
                print(f"Ошибка при вставке данных: {e}")
        elif user_pet in dogs_list:
            try:
                cursor.execute("UPDATE users SET user_dog = ? WHERE tg_id = ?", (user_pet, tg_id))
                conn.commit()
                print(f"Данные для tg_id {tg_id} успешно вставлены.")
            except sqlite3.Error as e:
                print(f"Ошибка при вставке данных: {e}")
        else:
            print("Ошибка при вставке данных: такой породы не существует")
        conn.close()
    else:
        print("Ошибка: пользователя с таким tg_id не существует")


def add_solo_user(tg_id, token):
    if check_tg_id_exists(tg_id):
        print("Ошибка: пользователь с таким tg_id уже существует")
    else:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (tg_id, token, secret_key) VALUES (?, ?, ?)", (tg_id, token, None))

        conn.commit()
        conn.close()


def add_main_family_user(tg_id, token, secret_key):
    if check_tg_id_exists(tg_id):
        print("Ошибка: пользователь с таким tg_id уже существует")
    else:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (tg_id, token, secret_key) VALUES (?, ?, ?)", (tg_id, token, secret_key))

        conn.commit()
        conn.close()


def add_other_family_user(tg_id, secret_key):
    if check_tg_id_exists(tg_id):
        print("Ошибка: пользователь с таким tg_id уже существует")
    else:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (tg_id, token, secret_key) VALUES (?, ?, ?)", (tg_id, None, secret_key))

        conn.commit()
        conn.close()


def get_token_by_tg_id(tg_id):
    conn = sqlite3.connect('users.db')
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
