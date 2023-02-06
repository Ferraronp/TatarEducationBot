from imports.imports import *
from tg.send_msg import *
import database.sql_commands


def echo(update, context, after_authorization=False):
    try:
        username = str(update.message.chat_id)
        blacklist = database.sql_commands.get_users_of_blacklist()
        if username in blacklist:
            print(f"\033[94m{datetime.datetime.now()}\033[0m", end=' ')
            print(username, update.message.text)
            return
        print(f"\033[93m{datetime.datetime.now()}\033[0m")
        print("PRINT_ECHO", username, update.message.text)
    except Exception:
        pass

    reply_keyboard = [['/help', '/close'],
                      ['🖋️Изменить логин/пароль', '📊Оценки'],
                      ['⏰✅Вкл. оповещения', '⏰❌Выкл. оповещения'],
                      ['📚Домашние задание', '📖Расписание'],
                      ['🏆Рейтинг'],
                      ['📝Создать примечание', '🗑️Удалить примечание']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)

    text = ("/close - закрыть клавиатуру\n" +
            "/start - смена логина и пароля\n"
            "/marks - вывод всех оценок\n" +
            "/set - включить оповещения об оценках\n" +
            "/unset - отключить уведомления\n" +
            "/homework - список домашних заданий на неделю\n" +
            "/schedule - расписание уроков\n" +
            "/addnote - создать примечание к уроку в расписание\n" +
            "/delnote - удалить примечание к уроку в расписание\n" +
            "/rating - рейтинг класса по среднему балла\n")

    """markup = InlineKeyboardMarkup([[InlineKeyboardButton(text='Скрыть', callback_data='unseen'),
                                    InlineKeyboardButton(text='Показать', callback_data='seen')]])
    text = '123'"""
    # bot.send_message(m.from_user.id, "Привет", reply_markup=markup)

    if after_authorization:
        text += "Авторизовано!\n"

    send_msg(update, text, markup)
