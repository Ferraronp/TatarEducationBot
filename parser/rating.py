from imports.imports import *
import parser.edu_login
import database.sql_commands


def update_rating(school: str, class_: str) -> None:
    list_of_pupils = database.sql_commands.get_list_of_rating(school, class_)
    list_of_pupils = sorted(list_of_pupils, key=lambda x: -x[1])
    t1 = None
    for i in list_of_pupils:
        password = database.sql_commands.get_password_by_login(i[0])
        # update_pupil(i[0], password)
        t1 = threading.Thread(target=update_pupil, args=(i[0], password), daemon=True)
        t1.start()
    if t1:
        t1.join()
    time.sleep(1)


def update_pupil(login, password):
    f = get_school_class_medium(login, password)
    database.sql_commands.update_pupil_in_db(login, *f)


def get_school_class_medium(login, password) -> (str, str):
    session = parser.edu_login.check(login, password)
    school = session.get('https://edu.tatar.ru/user/anketa/edit', timeout=120).text
    school = school.split('Школа:')[-1].split('<td>')[1].split('</td>')[0].strip()
    f = session.get('https://edu.tatar.ru/user/diary/term', timeout=120).text
    class_ = f.split("Класс: ")[-1].split('	</p>')[0].strip()
    try:
        medium = float(f.split('ИТОГО</strong></td><td>')[-1].split('</td>')[0])
    except ValueError:
        medium = 0.0
    return school, class_, medium


def init_list_of_ratings():
    users = set(database.sql_commands.get_password_login_where_can())
    t1 = None
    for i in users:
        t1 = threading.Thread(target=update_pupil, args=i, daemon=True)
        t1.start()
    if t1:
        t1.join()


def get_rating(userid: str):
    login, password = database.sql_commands.get_login_password(userid)
    f = get_school_class_medium(login, password)
    update_rating(f[0], f[1])

    ret = f'Рейтинг учеников\n__*_{f[1]}_*__ класса:\n'
    ratings = database.sql_commands.get_list_of_rating(f[0], f[1])
    ratings = sorted(ratings, key=lambda x: -x[1])
    for i, pupil in enumerate(ratings, start=1):
        ret += int(str(pupil[0]) == login) * '__*_' + str(i) + ") " + str(pupil[1]) + "_*__" * int(str(pupil[0]) == login) +\
               "\n"
    return ret
