from tg.handlers.support_functions.send_msg import *
import tg.database.sql_commands
from tg.handlers.support_functions.check_response import check_response


def print_schedule(update, context):
    """Вывод расписания по запросу"""
    username = str(update.message.chat_id)
    blacklist = tg.database.sql_commands.get_users_of_blacklist()
    if username in blacklist:
        logging.info(f"User in blacklist write message: {username}, {update.message.text}")
        return
    logging.info(f"User getting schedule: {username}")
    message_id = send_msg(update, "Собираем информацию...")
    try:
        text = get_text_to_print_schedule(username)
    except Exception:
        update_message(context, message_id, username, "Произошла ошибка, попробуйте заново через время")
        return
    else:
        update_message(context, message_id, username, text, parse_mode=ParseMode.MARKDOWN_V2)


def get_text_to_print_schedule(username) -> str or bool:
    user = tg.database.sql_commands.get_login_password(username)
    if not user:
        return False
    login, password = user
    date = datetime.datetime.now()
    urls = list()
    for i in range(-date.weekday(), 7 - date.weekday()):
        urls += [
            f"http://127.0.0.1:8000/homework/?login={login}&password={password}&date={int((date + datetime.timedelta(days=i)).timestamp())}"]
    req = (grequests.get(url) for url in urls)
    f = grequests.map(req)
    schedule = list(map(check_response, f))
    for x in schedule:
        if type(x) is str:
            return x
    # schedule = list(map(lambda x: x.json(), f))
    weekdays = ['__*_Понедельник_*__',
                '__*_Вторник_*__',
                '__*_Среда_*__',
                '__*_Четверг_*__',
                '__*_Пятница_*__',
                '__*_Суббота_*__',
                '__*_Воскресенье_*__']
    text = ''
    for i in range(7):  # День недели
        text += weekdays[i] + '\n'
        for j in range(len(schedule[i])):  # Номер урока
            text += schedule[i][j]['time'] + ' ' + schedule[i][j]['object'] + '\n'
        text += '\n'
    return text
