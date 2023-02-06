import sqlite3
import time


def add_login(username, login) -> None:
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    result = cur.execute(f"""SELECT * FROM users
                        WHERE username = '{username}'""").fetchone()
    if not result:
        cur.execute("""INSERT into users(username, login) values('{}', '{}')""".format(username, login))
    else:
        cur.execute(f"""UPDATE users
            set login = '{login}'
            WHERE username = '{username}'""")
    con.commit()
    con.close()


def add_password(username, password) -> None:
    con = sqlite3.connect("database/db.db")
    time.sleep(0.5)
    cur = con.cursor()
    time.sleep(0.5)
    cur.execute(f"""UPDATE users
        set password = '{password}'
        WHERE username = '{username}'""")
    con.commit()
    con.close()


def get_login_password(username: str) -> (str, str) or bool:
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    result = cur.execute(f"""SELECT login, password FROM users
                        WHERE username = '{username}'""").fetchone()
    con.commit()
    con.close()
    if not result:
        return False
    login = str(result[0])
    password = str(result[1])
    return login, password


def update_column_msg(username, status: int) -> None:
    """Status - 0 or 1"""
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    cur.execute(f"""UPDATE users
                    set msg = {status}
                    WHERE username = '{username}'""")
    con.commit()
    con.close()


def update_column_can(username, status: int) -> None:
    """Status - 0 or 1"""
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    cur.execute(f"""UPDATE users
                    set can = {status}
                    WHERE username = '{username}'""")
    con.commit()
    con.close()


def add_note_schedule(userid, day, num_of_lesson, note) -> None:
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    result = cur.execute(f"""SELECT * FROM notes_of_lessons
                                                WHERE username = '{userid}' and
                                                 day = {day} and
                                                  number_lesson={num_of_lesson}""").fetchall()
    if not result:
        cur.execute(f"""INSERT into notes_of_lessons(username, day, number_lesson, note)
                         values('{userid}', '{day}', '{num_of_lesson}', '{note}')""")
    else:
        cur.execute(f"""UPDATE notes_of_lessons
                                set note = '{note}'
                                WHERE username = '{userid}' and
                                 day = {day} and
                                  number_lesson = {num_of_lesson}""")
    con.commit()
    con.close()


def delete_note_schedule(userid, day, num_of_lesson) -> None:
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    result = cur.execute(f"""SELECT * FROM notes_of_lessons
                                                    WHERE username = '{userid}' and
                                                     day = {day} and number_lesson = {num_of_lesson}""").fetchall()
    if result:
        cur.execute(f"""DELETE from notes_of_lessons
                                    WHERE username = '{userid}' and
                                     day = {day} and
                                      number_lesson = {num_of_lesson}""")
    con.commit()
    con.close()


def get_notes_schedule(userid) -> list:
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    notes = cur.execute(f"""SELECT day, number_lesson, note FROM notes_of_lessons
                                WHERE username = '{userid}'""").fetchall()
    con.close()
    return notes


def get_column_can(userid) -> bool:
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    user = cur.execute(f"""SELECT can FROM users
                    WHERE username = '{userid}'""").fetchone()
    con.close()
    if not user:
        return False
    return bool(user[0] == 1)


def get_list_of_rating(school: str, clas: str) -> list:  # dict:
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    list_of_pupils = cur.execute(f"""SELECT login, medium FROM rating
                                    WHERE school = '{school}' and class = '{clas}'""").fetchall()
    con.close()
    return list_of_pupils


def get_password_by_login(login: str) -> str:
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    password = cur.execute(f"""SELECT login, password FROM users
                                        WHERE login = '{login}'""").fetchone()
    con.close()
    return password


def update_pupil_in_db(login: str, school: str, class_: str, medium: float) -> None:
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    result = cur.execute(f"""SELECT login FROM rating
                    WHERE login = '{login}'""").fetchone()
    if result:
        cur.execute(f"""UPDATE rating
               set school = '{school}', class = '{class_}', medium = {medium}
               WHERE login = '{login}'""")
    else:
        cur.execute(f"""INSERT into rating(login, school, class, medium) 
        values('{login}', '{school}', '{class_}', {medium})""")
    con.commit()
    con.close()


def get_password_login_where_can() -> list:
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    users = cur.execute(f"""SELECT login, password FROM users
                                    WHERE can = 1""").fetchall()
    con.close()
    return users


def get_password_login_where_msg() -> list:
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    users = cur.execute(f"""SELECT login, password FROM users
                                    WHERE msg = 1""").fetchall()
    con.close()
    return users


def get_school_class() -> list:
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    list_for_ratings = cur.execute("""SELECT school, class FROM rating""").fetchall()
    con.close()
    return list_for_ratings


def get_marks(userid: str) -> list:
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    marks = cur.execute(f"""SELECT * FROM marks
                    WHERE username = '{userid}'""").fetchall()
    con.close()
    return marks


def get_marks_by_object(userid: str, object_: str) -> list:
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    marks = cur.execute(f"""SELECT * FROM marks
                                    WHERE username = '{userid}' and object = '{object_}'""").fetchall()
    con.close()
    return marks


def add_marks(userid: str, object_: str, marks: str, medium: float) -> None:
    result = get_marks_by_object(userid, object_)
    if not result:
        con = sqlite3.connect("database/db.db")
        cur = con.cursor()
        cur.execute(f"""INSERT into marks(username, object, marks, medium)
             values('{userid}', '{object_}', '{marks}', {medium})""")
        con.commit()
        con.close()
    else:
        con = sqlite3.connect("database/db.db")
        cur = con.cursor()
        cur.execute(f"""UPDATE marks
                    set marks = '{marks}', medium = {medium}
                    WHERE username = '{userid}' and object = '{object_}'""")
        con.commit()
        con.close()


def get_userid_password_login_where_msg() -> list:
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    users = cur.execute(f"""SELECT username, login, password FROM users
                                    WHERE msg = 1""").fetchall()
    con.close()
    return users


def get_users_of_blacklist() -> list:
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    users = cur.execute(f"""SELECT username FROM blacklist""").fetchall()
    con.close()
    users = list(map(lambda x: str(x[0]), users))
    return users


def delete_marks(userid: str) -> None:
    con = sqlite3.connect("database/db.db")
    cur = con.cursor()
    cur.execute(f"""DELETE from marks
                    WHERE username = '{userid}'""")
    con.commit()
    con.close()
