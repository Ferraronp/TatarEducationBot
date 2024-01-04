from tg.imports.imports import *

import tg.database.sql_commands as sql_commands

from tg.handlers.echo import *
from tg.handlers.print_notice_marks import set_timer


def start(update, context):
    """Начало изменение(ввода) логина и пароля от аккаунта"""
    username = str(update.message.from_user.id)
    sql_commands.add_user(username)
    blacklist = sql_commands.get_users_of_blacklist()
    if username in blacklist:
        logging.info(f"User in blacklist write message: {username}, {update.message.text}")
        return ConversationHandler.END
    send_msg(update, "Введите свой логин от edu.tatar.ru")
    return 1


def get_login(update, context):
    username = str(update.message.from_user.id)
    login = update.message.text
    sql_commands.add_login(username, login)
    send_msg(update, "Введите свой пароль от edu.tatar.ru")
    return 2


def get_password(update, context):
    username = str(update.message.from_user.id)
    password = update.message.text
    sql_commands.add_password(username, password)
    login, password = sql_commands.get_login_password(username)
    url = 'http://127.0.0.1:8000/check'
    data = {"login": login, "password": password}
    f = grequests.get(url, params=data).send().response
    if f is None or f.status_code == 500:
        send_msg(update, "Произошла ошибка, попробуйте ещё раз через время")
        return start(update, context)
    ret = True if f.status_code == 200 else False
    if not ret:
        send_msg(update, "Не работает. Не верный логин или пароль")
        return start(update, context)

    sql_commands.delete_marks(username)

    echo(update, context, after_authorization=True)

    sql_commands.update_column_msg(username, 1)
    sql_commands.update_column_can(username, 1)

    set_timer(update, context)
    return ConversationHandler.END
