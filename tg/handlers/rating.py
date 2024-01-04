from tg.handlers.support_functions.send_msg import *
import tg.database.sql_commands

from tg.handlers.support_functions.check_response import check_response


def print_rating(update, context):
    """Вывод рейтинга учеников по среднему баллу"""
    username = str(update.message.from_user.id)
    blacklist = tg.database.sql_commands.get_users_of_blacklist()
    if username in blacklist:
        logging.info(f"User in blacklist write message: {username}, {update.message.text}")
        return
    logging.info(f"User getting rating: {username}")
    message_id = send_msg(update, "Собираем информацию...")
    try:
        msg = get_rating(username)
    except Exception:
        msg = "Произошла ошибка, попробуйте позже"
    update_message(context, message_id, username, msg, parse_mode=ParseMode.MARKDOWN_V2)


def get_rating(username: str) -> str:
    login, password = tg.database.sql_commands.get_login_password(username)
    url = 'http://127.0.0.1:8000/information'
    params = {"login": login, "password": password}
    rating_response = grequests.get(url, params=params).send().response
    data = check_response(rating_response)
    if type(data) is str:
        return data
    ret = f'Рейтинг учеников\n__*_{data[1]}_*__ класса:\n'
    ratings = tg.database.sql_commands.get_list_of_rating(data[0], data[1])
    ratings = sorted(ratings, key=lambda x: -x[1])
    for i, pupil in enumerate(ratings, start=1):
        ret += int(str(pupil[0]) == login) * '__*_' + str(i) + ") " + str(pupil[1]) + "_*__" * int(str(pupil[0]) == login) +\
               "\n"
    return ret
