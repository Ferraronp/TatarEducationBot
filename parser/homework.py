from imports.imports import *
import parser.edu_login
import database.sql_commands


def get_html_homeworks(session, urls: list) -> list or bool:
    f = (grequests.get(url, session=session) for url in urls)
    post_request = []
    for i, res in enumerate(grequests.map(f)):
        post_request += [res.text]
    session.close()
    return post_request


def get_urls(kwargs):
    some_date = datetime.datetime(2022, 10, 5).date()
    now_date = datetime.datetime.today().date()
    some_date_edu = 1664917200
    a = (now_date - some_date).days
    delta = 24 * 60 * 60  # перевод из дней в секунды
    if 'delta' not in kwargs:
        kwargs['delta'] = 0
    if kwargs['delta'] % 7 != 0:
        kwargs['delta'] += 7 - (kwargs['delta'] % 7)

    urls = []
    for i in range(0 - kwargs['delta'], 7 - kwargs['delta']):
        urls += [f'https://edu.tatar.ru/user/diary/day?for={str(some_date_edu + (a + i) * delta)}']
    return urls


def parse_day_homework(text: str or bool) -> list | bool:
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

    text = list(map(lambda x:
                    [x[0].replace('\n', ' '), x[1].replace('\n', ' '), x[2].replace('\n', ' ')],
                    text))
    text = list(map(lambda x: list(map(lambda y: y.replace('<br />', '').replace('\r', ''), x)), text))
    return text


def get_all_homework(userid: str, **kwargs) -> dict | bool:
    user = database.sql_commands.get_login_password(userid)
    if not user:
        return False
    login, password = user
    session = parser.edu_login.check(login, password)
    if not session:
        return False

    urls = get_urls(kwargs)
    sp = get_html_homeworks(session, urls)

    day_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    now_date = datetime.datetime.today().date()
    ret = {}
    for i in range(0 - kwargs['delta'], 7 - kwargs['delta']):
        day = (now_date.weekday() + i) % 7
        date = (datetime.datetime.today() + datetime.timedelta(days=i)).strftime("%d.%m")
        homework = parse_day_homework(sp[i])
        if type(homework) == bool:
            return False
        ret[f"__*_{day_week[day]}_*__ {str(date)}"] = list(map(lambda x:
                                                               list(map(lambda y: y.replace("_", "\\_"), x)),
                                                               homework))
    return ret


def get_homework(userid: str) -> list | bool:
    sp: dict = get_all_homework(userid)
    if not sp:
        return False
    send = []
    for i, key in enumerate(sp):
        send += [key + "\n" + "\n\n".join(list(map(lambda x: '\n'.join(x), sp[key])))]

    return send[::-1]


def get_day_homework(userid: str, date: datetime.datetime.date) -> str | bool:
    some_date = datetime.datetime(2022, 10, 5).date()
    some_date_edu = 1664917200
    a = (date - some_date).days
    delta = 24 * 60 * 60  # перевод из дней в секунды
    url = [f'https://edu.tatar.ru/user/diary/day?for={str(some_date_edu + a * delta)}']

    user = database.sql_commands.get_login_password(userid)
    if not user:
        return False
    login, password = user
    session = parser.edu_login.check(login, password)
    if not session:
        return False

    html_homework = get_html_homeworks(session, url)[0]

    day_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    day = date.weekday()
    date = date.strftime("%d.%m.%y")
    homework = parse_day_homework(html_homework)
    if type(homework) == bool:
        return False
    homework = list(map(lambda x:
                    list(map(lambda y: y.replace("_", "\\_"), x)),
                    homework))
    day_to_text = f"{day_week[day]} {str(date)}"
    text = day_to_text + "\n" + "\n\n".join(list(map(lambda x: '\n'.join(x), homework)))
    return text


def get_day_from_homework(text: str) -> datetime.datetime.date:
    date = list(map(int, text.split("\n")[0].split()[1].split('.')))
    return datetime.datetime(2000 + date[2], date[1], date[0]).date()
