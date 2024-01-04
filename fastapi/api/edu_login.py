import grequests
from api.cookies import get_cookie_from_db, update_cookie_in_db
from fastapi import HTTPException


def update_cookie(login: str, password: str) -> None:
    """
    :param login: логин от edu.tatar.ru
    :param password: пароль от edu.tatar.ru
    """
    url = 'https://edu.tatar.ru/logon'
    user_agent_val = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                     'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    headers = {'Referer': url, 'User-Agent': user_agent_val}

    response = grequests.post(url, data={
        'backUrl': 'https://edu.tatar.ru',
        'main_login2': login,
        'main_password2': password,
    }, timeout=120, headers=headers).send().response

    if response.status_code != 200:  # Не работает сервер
        raise HTTPException(status_code=500, detail="Server error")
    if 'заблокирован' in response.text:  # Проблема со входом
        raise HTTPException(status_code=500, detail="Server error")
    if 'Войти в учётную запись EDU' in response.text:  # Неверный логин/пароль
        raise HTTPException(status_code=400, detail="Invalid login or password")
    if 'Мой дневник' not in response.text:  # Уже не ученик
        raise HTTPException(status_code=400, detail="Invalid login or password")
    update_cookie_in_db(login, password, response.cookies["DNSID"])


def get_url(login: str, password: str, url: str, second_chance: bool = False):
    cookies = get_cookie_from_db(login, password)
    if cookies is None:
        if second_chance:
            raise HTTPException(status_code=500, detail="Server error")
        update_cookie(login, password)
        return get_url(login, password, url, second_chance=True)
    cookies = {"HLP": '', "DNSID": cookies[0]}
    response = grequests.get(url, cookies=cookies).send().response
    if response.status_code != 200:  # Не работает сервер
        raise HTTPException(status_code=500, detail="Server error")
    if 'заблокирован' in response.text:  # Проблема со входом
        raise HTTPException(status_code=500, detail="Server error")
    if 'Войти в учётную запись EDU' in response.text:  # Неверный логин/пароль
        if second_chance:
            raise HTTPException(status_code=400, detail="Invalid login or password")
        update_cookie(login, password)
        return get_url(login, password, url, second_chance=True)
    if "Вход для пользователей" in response.text:  # Куки закончились
        if second_chance:  # Произошла ошибка со входом
            raise HTTPException(status_code=500, detail="Server error")
        update_cookie(login, password)
        return get_url(login, password, url, second_chance=True)
    return response.text.replace('&mdash;', '-')


def get_urls(login: str, password: str, urls: list[str], second_chance: bool = False):
    cookies = get_cookie_from_db(login, password)
    if cookies is None:
        if second_chance:
            raise HTTPException(status_code=500, detail="Server error")
        update_cookie(login, password)
        return get_urls(login, password, urls, second_chance=True)
    cookies = {"HLP": '', "DNSID": cookies[0]}
    requests = (grequests.get(url, cookies=cookies) for url in urls)
    response_texts = list()
    for response in grequests.map(requests):
        if response.status_code != 200:  # Не работает сервер
            raise HTTPException(status_code=500, detail="Server error")
        if 'заблокирован' in response.text:  # Проблема со входом
            raise HTTPException(status_code=500, detail="Server error")
        if 'Войти в учётную запись EDU' in response.text:  # Неверный логин/пароль
            if second_chance:
                raise HTTPException(status_code=400, detail="Invalid login or password")
            update_cookie(login, password)
            return get_urls(login, password, urls, second_chance=True)
        if "Вход для пользователей" in response.text:  # Куки закончились
            if second_chance:  # Произошла ошибка со входом
                raise HTTPException(status_code=500, detail="Server error")
            update_cookie(login, password)
            return get_urls(login, password, urls, second_chance=True)
        response_texts.append(response.text.replace('&mdash;', '-'))
    return response_texts
