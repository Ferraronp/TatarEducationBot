from tg.handlers.support_functions.send_msg import *
import tg.database.sql_commands


def echo(update, context, after_authorization=False):
    """
    Выводит подсказку по командам и клавиатуру
    :param after_authorization: Если True, добавит в конце "Авторизовано!"
    """
    try:
        username = str(update.message.chat_id)
        blacklist = tg.database.sql_commands.get_users_of_blacklist()
        if username in blacklist:
            logging.info(f"User in blacklist write message: {username}, {update.message.text}")
            return
        logging.info(f"User write message: {username}, {update.message.text}")
    except Exception:
        pass

    reply_keyboard = [['/help', '/close'],
                      ['🖋️Изменить логин/пароль', '📊Оценки'],
                      ['⏰✅Вкл. оповещения', '⏰❌Выкл. оповещения'],
                      ['📚Домашние задание', '📖Расписание'],
                      ['🏆Рейтинг']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)

    text = ("/close - закрыть клавиатуру\n" +
            "/start - смена логина и пароля\n"
            "/marks - вывод всех оценок\n" +
            "/set - включить оповещения об оценках\n" +
            "/unset - отключить уведомления\n" +
            "/homework - список домашних заданий на неделю\n" +
            "/schedule - расписание уроков\n" +
            "/rating - рейтинг класса по среднему балла\n")

    if after_authorization:
        text += "Авторизовано!\n"

    send_msg(update, text, markup)
