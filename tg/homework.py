from imports.imports import *
from parser.homework import *
from tg.send_msg import *


'''def print_homework(update, context):
    userid = str(update.message.chat_id)
    blacklist = database.sql_commands.get_users_of_blacklist()
    if userid in blacklist:
        print(f"\033[94m{datetime.datetime.now()}\033[0m", end=' ')
        print(userid, update.message.text)
        return
    print(f"\033[93m{datetime.datetime.now()}\033[0m")
    print("PRINT_HOMEWORK " + str(userid))
    text = get_homework(userid)
    if not text:
        send_msg(update, userid, 'Произошла ошибка')
        return
    for i in range(len(text)):
        send_msg_with_parse_mode(context, userid, text[i])'''


def print_homework(update, context):
    userid = str(update.message.chat_id)
    blacklist = database.sql_commands.get_users_of_blacklist()
    if userid in blacklist:
        print(f"\033[94m{datetime.datetime.now()}\033[0m", end=' ')
        print(userid, update.message.text)
        return
    print(f"\033[93m{datetime.datetime.now()}\033[0m")
    print("PRINT_HOMEWORK " + str(userid))

    text = get_day_homework(userid, datetime.datetime.now())
    if not text:
        send_msg(update, 'Произошла ошибка')
        return
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(text='Предыдущий день', callback_data='previous_day_homework'),
                                    InlineKeyboardButton(text='Следующий день', callback_data='next_day_homework')]])
    send_msg(update, text, markup)
