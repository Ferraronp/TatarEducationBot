from imports.imports import *

sessions = dict()


def check(login, password, **kwargs):
    global sessions
    first_code = 0
    second_code = 0
    post_request = ""
    session = ...
    while first_code != 200 or second_code != 200:
        url = 'https://edu.tatar.ru/logon'
        user_agent_val = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        if login not in sessions:
            session = grequests.Session()
            sessions[login] = session
        else:
            session = sessions[login]
        # with grequests.Session() as session:
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
        # session.close()
        if 'Должность' in post_request:
            second_code = 400
    # if 'class="table term-marks"' not in post_request:
    if 'Войти в учётную запись EDU' in post_request:
        return False
    return session
