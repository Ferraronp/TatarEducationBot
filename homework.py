import inspect
import sqlite3
import time
import datetime

from telegram import ParseMode


def get_html_homeworks(login: str, password: str, urls: list) -> list or bool:
    import grequests
    # import requests
    first_code = 0
    post_request = ""
    while first_code != 200:
        url = 'https://edu.tatar.ru/logon'
        user_agent_val = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        with grequests.Session() as session:
        # with requests.Session() as session:
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

            f = (grequests.get(url, session=session) for url in urls)
            post_request = []
            for i, res in enumerate(grequests.map(f)):
                post_request += [res.text]
            # post_request = [session.get(url).text for url in urls]
            session.close()
    if 'Выход' not in post_request[-1]:
        return False
    return post_request


def get_day_homework(text: str or bool) -> list or bool:
    if type(text) == bool:
        return False
    text = text.split("<tbody>")[-1].split("</tbody>")[0].replace("&mdash;", '-').replace("<br/>", '')
    text = "\n".join(text.replace('\t', '').split("\n"))
    text = text.split('<tr style="text-align: center;">')
    text = list(map(lambda x: x.split("</td>")[:3], text))[1:]
    text = list(map(lambda x: list(map(lambda y: y.split('<td style="vertical-align: middle;">')[-1], x)), text))
    text = list(map(lambda x: list(map(lambda y: y.split('<p>')[-1].split("</p>")[0].strip(), x)), text))
    text = list(map(lambda x: x[:2] + ["".join(list(map(lambda y:
                                                        y.split('<a target="_blank" '
                                                                'rel="noopener noreferrer"\nhref="')[0],
                                                        x[2].replace('</a>', '').split('">'))))], text))
    # for i in range(len(text)):
    # text[i][2] = "".join(list(map(lambda y: y.split('<a target="_blank" rel="noopener noreferrer"\nhref="')[0],
    # text[i][2].replace('</a>', '').split('">'))))
    try:
        f = len(max(text, key=lambda x: len(x[1]))[1])
    except ValueError:
        f = 0
    # text = list(map(lambda x: f"{x[0]} {x[1]} {' ' * (f - len(x[1]))} {x[2]}".replace('\n', ' '), text))
    # return "\n".join(text).replace('<br />', '').replace('\r', '')
    """text = list(map(lambda x:
                    [x[0].replace('\n', ' '), x[1].replace('\n', ' ') + ' ' * (f - len(x[1])), x[2].replace('\n', ' ')],
                    text))"""
    text = list(map(lambda x:
                    [x[0].replace('\n', ' '), x[1].replace('\n', ' '), x[2].replace('\n', ' ')],
                    text))
    text = list(map(lambda x: list(map(lambda y: y.replace('<br />', '').replace('\r', ''), x)), text))
    return text


def get_all_homework(userid: str, **kwargs) -> dict or bool:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    login, password = cur.execute(f"""SELECT login, password FROM users
            WHERE username = '{userid}'""").fetchone()
    con.close()

    some_date = datetime.datetime(2022, 10, 5).date()
    now_date = datetime.datetime.today().date()
    some_date_edu = 1664917200
    a = (now_date - some_date).days
    delta = 24 * 60 * 60
    day_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    if 'delta' not in kwargs:
        kwargs['delta'] = 0
    if kwargs['delta'] % 7 != 0:
        kwargs['delta'] += 7 - (kwargs['delta'] % 7)

    urls = []
    for i in range(0 - kwargs['delta'], 7 - kwargs['delta']):
        urls += [f'https://edu.tatar.ru/user/diary/day?for={str(some_date_edu + (a + i) * delta)}']
    sp = get_html_homeworks(login, password, urls)
    if type(sp) == bool:
        return False
    """ret = []
    for i in range(7):
        day = (now_date.weekday() + i) % 7
        date = (datetime.today() + timedelta(days=i)).strftime("%d.%m")
        ret += [f"{day_week[day] + ' ' + str(date)}\n{get_day_homework(sp[i])}"]
    return "\n\n".join(ret)"""
    ret = {}
    for i in range(0 - kwargs['delta'], 7 - kwargs['delta']):
        day = (now_date.weekday() + i) % 7
        date = (datetime.datetime.today() + datetime.timedelta(days=i)).strftime("%d.%m")
        homework = get_day_homework(sp[i])
        if type(homework) == bool:
            return False
        ret[f"__*_{day_week[day]}_*__ {str(date)}"] = list(map(lambda x:
                                                               list(map(lambda y: y.replace("_", "\\_"), x)),
                                                               homework))
    return ret


def get_homework(userid: str) -> list or bool:
    sp: dict = get_all_homework(userid)
    if type(sp) == bool:
        return False
    send = []
    for i, key in enumerate(sp):
        send += [key + "\n" + "\n\n".join(list(map(lambda x: '\n'.join(x), sp[key])))]
    # send = "\n\n".join(send)
    return send[::-1]


def print_homework(update, context):
    userid = update.message.chat_id
    text = get_homework(userid)
    if not text:
        send_msg(context, userid, 'Произошла ошибка')
        return
    for i in range(len(text)):
        send_msg(context, userid, text[i])


def send_msg(context, userid: str, msg: str):
    msg = msg.replace('=', '\\=').replace('-', '\\-').replace('(', '\\(').replace(')', '\\)').replace('+', '\\+')
    msg = msg.replace('.', '\\.').replace('!', '\\!')
    sent = False
    while not sent:
        try:
            context.bot.send_message(userid, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
            sent = True
        except Exception as ex:
            func_name = inspect.currentframe().f_back.f_code.co_name
            print(f"\033[91m{datetime.datetime.now()} Error in homework.py in {func_name}\033[0m"
                  f"\n{ex}\n{userid}\n{[msg]}")
            time.sleep(10)
