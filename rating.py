import sqlite3
import time
import datetime
import inspect
from telegram import ParseMode
from edu_login import check
import threading


def update_rating(school: str, clas: str) -> None:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    list_of_pupils = cur.execute(f"""SELECT login FROM rating
                            WHERE school = '{school}' and class = '{clas}'""").fetchall()
    con.close()
    for i in list_of_pupils:
        con = sqlite3.connect("db.db")
        cur = con.cursor()
        i = i[0]
        pupil = cur.execute(f"""SELECT login, password FROM users
                                    WHERE login = '{i}'""").fetchone()
        con.close()
        # f = get_school_class_medium(*pupil)
        # update_pupil_in_db(pupil[0], *f)
        t1 = threading.Thread(target=update_pupil, args=pupil, daemon=True)
        t1.start()
    t1.join()


def update_pupil(login, password):
    f = get_school_class_medium(login, password)
    update_pupil_in_db(login, *f)


def update_all_ratings():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    list_for_ratings = set(cur.execute("""SELECT school, class FROM rating""").fetchall())
    con.close()
    for i in list_for_ratings:
        t1 = threading.Thread(target=update_rating, args=i, daemon=True)
        t1.start()
    t1.join()


def get_school_class_medium(login, password) -> (str, str):
    school = check(login, password, url='https://edu.tatar.ru/user/anketa/edit')
    school = school.split('Школа:')[-1].split('<td>')[1].split('</td>')[0].strip()
    f = check(login, password, url='https://edu.tatar.ru/user/diary/term')
    clas = f.split("Класс: ")[-1].split('	</p>')[0].strip()
    try:
        medium = float(f.split('ИТОГО</strong></td><td>')[-1].split('</td>')[0])
    except ValueError:
        medium = 0.0
    return school, clas, medium


def update_pupil_in_db(login: str, school: str, clas: str, medium: float) -> None:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    result = cur.execute(f"""SELECT login FROM rating
                    WHERE login = '{login}'""").fetchone()
    if result:
        cur.execute(f"""UPDATE rating
               set school = '{school}', class = '{clas}', medium = {medium}
               WHERE login = '{login}'""")
    else:
        cur.execute(f"""INSERT into rating(login, school, class, medium) 
        values('{login}', '{school}', '{clas}', {medium})""")
    con.commit()
    con.close()


def init_list_of_ratings():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    users = set(cur.execute(f"""SELECT login, password FROM users
                                WHERE can = 1""").fetchall())
    con.close()

    for i in users:
        f = get_school_class_medium(*i)
        update_pupil_in_db(i[0], *f)


def get_list_of_rating(school: str, clas: str) -> list:  # dict:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    list_of_pupils = cur.execute(f"""SELECT login, medium FROM rating
                                    WHERE school = '{school}' and class = '{clas}'""").fetchall()
    con.close()
    list_of_pupils = sorted(list_of_pupils, key=lambda x: -x[1])
    return list_of_pupils


def get_rating(userid: str):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    user = cur.execute(f"""SELECT login, password FROM users
            WHERE username = '{userid}'""").fetchone()
    con.close()
    f = get_school_class_medium(*user)
    update_rating(f[0], f[1])

    ret = f'Рейтинг учеников\n__*_{f[1]}_*__ класса:\n'
    for i, pupil in enumerate(get_list_of_rating(f[0], f[1]), start=1):
        ret += int(pupil[0] == user[0]) * '__*_' + str(i) + ") " + str(pupil[1]) + "_*__" * int(pupil[0] == user[0]) +\
               "\n"
    return ret


def print_rating(update, context):
    userid = str(update.message.from_user.id)
    print(f"\033[93m{datetime.datetime.now()}\033[0m")
    print("PRINT_RATING " + userid)

    con = sqlite3.connect("db.db")
    cur = con.cursor()
    user = cur.execute(f"""SELECT can FROM users
                WHERE username = '{userid}'""").fetchone()
    con.close()
    if user[0] == 1:
        msg = get_rating(userid)
    else:
        msg = 'ERROR'
    send_msg(context, userid, msg)


def send_msg(context, userid: str, msg: str):
    error = False
    msg = msg.replace(".", "\\.").replace(")", "\\)")
    # print(f"\033[93m{datetime.datetime.now()}\033[0m")
    print(f"\033[93m{datetime.datetime.now()}\033[0m", end=' ')
    try:
        print(userid)
    except Exception:
        pass
    print([msg])
    sent = False
    while not sent:
        try:
            context.bot.send_message(userid, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
            sent = True
        except Exception as ex:
            func_name = inspect.currentframe().f_back.f_code.co_name
            print(f"\033[91m{datetime.datetime.now()} Error bot.send_message in rating.py"
                  f" in {func_name}\033[0m"
                  f"\n{ex}\n{userid}\n{[msg]}")
            time.sleep(10)
            error = True
    if error:
        print("Отправлено")
