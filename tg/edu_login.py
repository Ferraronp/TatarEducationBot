from string import ascii_letters
from random import choice

from imports.imports import *

from database.sql_commands import *

from tg.echo import *
from tg.print_notice_marks import set_timer

from parser.edu_login import *
from parser.rating import update_pupil


def start(update, context):
    import requests
    username = str(update.message.from_user.id)
    blacklist = database.sql_commands.get_users_of_blacklist()
    if username in blacklist:
        print(f"\033[94m{datetime.datetime.now()}\033[0m", end=' ')
        print(username, update.message.text)
        return ConversationHandler.END

    secret_word = ''
    for _ in range(32):
        secret_word += choice(ascii_letters)

    requests.post(f'https://Ferraronp.pythonanywhere.com/post/{secret_word}/604831762')
    msg = f'Введите свой логин и пароль'
    url = f'https://Ferraronp.pythonanywhere.com/form/{secret_word}'
    buttons = [[InlineKeyboardButton(text='Авторизоваться', url=url)]]
    markup = InlineKeyboardMarkup(buttons)
    send_msg(update, msg, markup)

    a = requests.get(f'https://Ferraronp.pythonanywhere.com/get/{secret_word}').json()
    while not a['result']:
        time.sleep(5)
        a = requests.get(f'https://Ferraronp.pythonanywhere.com/get/{secret_word}').json()
    print(a['login'], a['password'])
    login, password = a['login'], a['password']
    try:
        ret = check(login, password)
    except Exception as ex:
        print(f"\033[91m{datetime.datetime.now()} Error in telegram.get_password\033[0m\n{ex}")
        ret = False
    if not ret:
        send_msg(update, "Не работает. Не верный логин или пароль")
        return start(update, context)

    delete_marks(username)
    add_login(username, login)
    add_password(username, password)

    echo(update, context, after_authorization=True)

    update_column_msg(username, 1)
    update_column_can(username, 1)

    update_pupil(login, password)

    set_timer(update, context)
    return ConversationHandler.END


'''def start(update, context):
    username = str(update.message.from_user.id)
    blacklist = database.sql_commands.get_users_of_blacklist()
    if username in blacklist:
        print(f"\033[94m{datetime.datetime.now()}\033[0m", end=' ')
        print(username, update.message.text)
        return ConversationHandler.END
    send_msg(update, "Введите свой логин от edu.tatar.ru")
    return 1'''


def get_login(update, context):
    username = str(update.message.from_user.id)
    login = update.message.text
    add_login(username, login)
    send_msg(update, "Введите свой пароль от edu.tatar.ru")
    return 2


def get_password(update, context):
    username = str(update.message.from_user.id)
    password = update.message.text
    add_password(username, password)
    login, password = get_login_password(username)

    try:
        ret = check(login, password)
    except Exception as ex:
        print(f"\033[91m{datetime.datetime.now()} Error in telegram.get_password\033[0m\n{ex}")
        ret = False
    if not ret:
        send_msg(update, "Не работает. Не верный логин или пароль")
        return start(update, context)

    echo(update, context, after_authorization=True)

    update_column_msg(username, 1)
    update_column_can(username, 1)

    update_pupil(login, password)

    set_timer(update, context)
    return ConversationHandler.END
