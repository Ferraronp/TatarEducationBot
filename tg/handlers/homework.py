import tg.database.sql_commands
from tg.handlers.support_functions.send_msg import *

from tg.handlers.support_functions.check_response import check_response


def get_text_to_print(homeworks: list, date: datetime.datetime) -> str:
    weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    text = weekdays[date.weekday()] + ' ' + str(date.day) + '.' + str(date.month) + '.' + str(date.year) + '\n'
    for lesson in homeworks:
        text += lesson['time'] + '\n__*_' + lesson['object'] + '_*__\n' + lesson['homework'] + '\n\n'
    return text


def print_homework(update, context):
    username = str(update.message.chat_id)
    blacklist = tg.database.sql_commands.get_users_of_blacklist()
    if username in blacklist:
        logging.info(f"User in blacklist write message: {username}, {update.message.text}")
        return
    logging.info(f"User getting homework: {username}")
    user = tg.database.sql_commands.get_login_password(username)
    if not user:
        send_msg(update, 'Введите /start для ввода логина и пароля')
        return
    login, password = user
    message_id = send_msg(update, 'Собираем информацию...')
    url = 'http://127.0.0.1:8000/homework'
    params = {"login": login, "password": password, "date": int(datetime.datetime.now().timestamp())}
    homeworks_response = grequests.get(url, params=params).send().response
    data = check_response(homeworks_response)
    if type(data) is str:
        update_message(context, message_id, username, data)
        return
    '''if homeworks_response.status_code in [400, 500]:
        update_message(context, message_id, username, "Произошла ошибка, попробуйте ещё раз через время")
        return'''
    text = get_text_to_print(data, datetime.datetime.now())
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(text='Предыдущий день', callback_data='previous_day_homework'),
                                    InlineKeyboardButton(text='Следующий день', callback_data='next_day_homework')]])
    update_message(context, message_id, username, text, markup, ParseMode.MARKDOWN_V2)


def callback(update, context):
    """
    Меняет текст домашнего задания при нажатии на кнопку "след. день" или "пред. день"
    """
    dict_ = update.to_dict()
    text_button = dict_['callback_query']['data']
    if text_button == 'next_day_homework' or text_button == 'previous_day_homework':
        username = update.effective_user['id']
        message_id = dict_['callback_query']['message']['message_id']
        message = dict_['callback_query']['message']['text']
        user = tg.database.sql_commands.get_login_password(username)
        if not user:
            return
        update_message(context, message_id, username, "Собираем информацию...")
        login, password = user
        date = get_day_from_message(message) + datetime.timedelta(days=1 if text_button == 'next_day_homework' else -1)
        url = 'http://127.0.0.1:8000/homework'
        params = {"login": login, "password": password, "date": int(date.timestamp())}
        homeworks_response = grequests.get(url, params=params).send().response
        data = check_response(homeworks_response)
        if type(data) is str:
            update_message(context, message_id, username, data)
            return
        '''if homeworks_response.status_code in [400, 500]:
            update_message(context, message_id, username, "Произошла ошибка, попробуйте заново через время")
            return
        homeworks = homeworks_response.json()'''
        homeworks = list(map(lambda x: {"object": x["object"].replace("*", "\\*"),
                                        "homework": x["homework"].replace("*", "\\*"),
                                        "time": x["time"].replace("*", "\\*")}, data))
        text = get_text_to_print(homeworks, date)
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(text='Предыдущий день',
                                                             callback_data='previous_day_homework'),
                                        InlineKeyboardButton(text='Следующий день',
                                                             callback_data='next_day_homework')]])
        update_message(context, message_id, username, text, markup, ParseMode.MARKDOWN_V2)


def get_day_from_message(text: str) -> datetime.datetime:
    date = list(map(int, text.split("\n")[0].split()[1].split('.')))
    return datetime.datetime(date[2], date[1], date[0])
