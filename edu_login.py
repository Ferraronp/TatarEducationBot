import sqlite3
import time
import datetime
import inspect
from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler


def start(update, context):
    send_msg(update, "Введите свой логин от edu.tatar.ru")
    return 1


def get_login(update, context):
    login = update.message.text
    username = str(update.message.from_user.id)
    con = sqlite3.connect("db.db")
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
    send_msg(update, "Введите свой пароль от edu.tatar.ru")
    return 2


def get_password(update, context):
    password = update.message.text
    username = str(update.message.from_user.id)
    con = sqlite3.connect("db.db")
    time.sleep(0.5)
    cur = con.cursor()
    time.sleep(0.5)
    cur.execute(f"""UPDATE users
    set password = '{password}'
    WHERE username = '{username}'""")

    result = cur.execute(f"""SELECT login, password FROM users
                WHERE username = '{username}'""").fetchone()
    login = str(result[0])
    password = str(result[1])
    con.commit()
    con.close()
    try:
        ret = check(login, password)
    except Exception as ex:
        func_name = inspect.currentframe().f_back.f_code.co_name
        print(f"\033[91m{datetime.datetime.now()} Error bot.send_message in edu_login.py in {func_name}\033[0m\n{ex}")
        ret = False
    if not ret:
        send_msg(update, "Не работает. Не верный логин или пароль")
        return start(update, context)
    """reply_keyboard = [['/help', '/close'],
                      ['/start', '/marks'],
                      ['/set', '/unset'],
                      ['/homework', '/schedule'],
                      ['/addnote', '/delnote']]"""

    reply_keyboard = [['/help', '/close'],
                      ['🖋️Изменить логин/пароль', '📊Оценки'],
                      ['⏰✅Вкл. оповещения', '⏰❌Выкл. оповещения'],
                      ['📚Домашние задание', '📖Расписание'],
                      ['📝Создать примечание', '🗑️Удалить примечание']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
    send_msg(update, "Авторизовано!\n" +
             "/close - закрыть клавиатуру\n" +
             "/start - смена логина и пароля\n/marks - вывод всех оценок\n" +
             "/set - включить оповещения об оценках\n/unset - отключить уведомления\n" +
             "/homework - список домашних заданий на неделю\n/schedule - расписание уроков\n" +
             "/addnote - создать примечание к уроку в расписание\n" +
             "/delnote - удалить примечание к уроку в расписание",
             markup)

    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute(f"""UPDATE users
                set can = 1, msg = 1
                WHERE username = '{username}'""")
    con.commit()
    con.close()
    from print_notice_marks import set_timer
    set_timer(update, context)
    return ConversationHandler.END


def check(login, password, **kwargs):
    # import grequests
    import requests
    first_code = 0
    second_code = 0
    post_request = ""
    while first_code != 200 or second_code != 200:
        url = 'https://edu.tatar.ru/logon'
        user_agent_val = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        # session = grequests.Session()
        # with grequests.Session() as session:
        with requests.Session() as session:
            r = session.get(url, headers={
                'User-Agent': user_agent_val
            }, timeout=120)
            first_code = r.status_code
            session.headers.update({'Referer': url})
            session.headers.update({'User-Agent': user_agent_val})
            session.post(url, {
                'backUrl': 'https://edu.tatar.ru',
                'main_login2': login,
                'main_password2': password,
            }, timeout=120)
            url2 = "https://edu.tatar.ru/user/diary/term"
            if 'url' in kwargs:
                url2 = kwargs['url']
            post_request = session.get(url2, timeout=120)
            second_code = post_request.status_code
            post_request = post_request.text
            session.close()
            if 'Должность' in post_request:
                second_code = 400
    # if 'class="table term-marks"' not in post_request:
    if 'Выход' not in post_request:
        return False
    return post_request


def send_msg(update, msg, markup=None):
    sent = False
    while not sent:
        try:
            update.message.reply_text(msg, reply_markup=markup)
            sent = True
        except Exception as ex:
            func_name = inspect.currentframe().f_back.f_code.co_name
            print(f"\033[91m{datetime.datetime.now()} Error bot.send_message in edu_login.py in {func_name}\033[0m\n{ex}")
            time.sleep(10)
