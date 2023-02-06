from imports.imports import *
import parser.schedule
from tg.send_msg import *
import database.sql_commands


def print_schedule(update, context):
    userid = str(update.message.chat_id)
    blacklist = database.sql_commands.get_users_of_blacklist()
    if userid in blacklist:
        print(f"\033[94m{datetime.datetime.now()}\033[0m", end=' ')
        print(userid, update.message.text)
        return
    print(f"\033[93m{datetime.datetime.now()}\033[0m")
    print("PRINT_SCHEDULE " + str(userid))
    text = parser.schedule.get_schedule(userid)
    if not text:
        send_msg_with_parse_mode(context, userid, 'Произошла ошибка')
        return
    send_msg_with_parse_mode(context, userid, text)


def add_note_to_schedule(update, context):
    userid = str(update.message.chat_id)
    blacklist = database.sql_commands.get_users_of_blacklist()
    if userid in blacklist:
        print(f"\033[94m{datetime.datetime.now()}\033[0m", end=' ')
        print(userid, update.message.text)
        return ConversationHandler.END
    print(f"\033[93m{datetime.datetime.now()}\033[0m")
    print("ADD_NOTE " + str(userid))
    send_msg_with_parse_mode(context, userid, "Создание примечания\nВведите номер дня недели(1, 2, ...)\n/close - для отмены")
    return 1


def get_day_add_note_schedule(update, context):
    userid = update.message.chat_id
    day = update.message.text
    if day == '/close':
        send_msg_with_parse_mode(context, userid, "Создание примечания отменено")
        return ConversationHandler.END
    try:
        day = int(day)
        if not (1 <= day <= 7):
            raise ValueError
        context.user_data['day'] = day
        send_msg_with_parse_mode(context, userid, "Введите номер урока по расписанию(1, 2, ...)\n/close - для отмены")
    except ValueError:
        send_msg_with_parse_mode(context, userid, "Некорректно введён день.\nВведите номер дня недели(1, 2, ...)\n/close - для отмены")
        return 1
    return 2


def get_num_of_lesson_add_note_schedule(update, context):
    userid = update.message.chat_id
    num_of_lesson = update.message.text
    if num_of_lesson == '/close':
        send_msg_with_parse_mode(context, userid, "Создание примечания отменено")
        return ConversationHandler.END
    try:
        num_of_lesson = int(num_of_lesson)
        if not (1 <= num_of_lesson):
            raise ValueError
        context.user_data['num_of_lesson'] = num_of_lesson
        day = context.user_data.get('day', False)
        day_week = {1: "Понедельник",
                    2: "Вторник",
                    3: "Среда",
                    4: "Четверг",
                    5: "Пятница",
                    6: "Суббота",
                    7: "Воскресенье"}
        send_msg_with_parse_mode(context, userid, f"Введите примечание к {num_of_lesson} уроку в {day_week[day]}\n/close - для отмены")
    except ValueError:
        send_msg_with_parse_mode(context, userid, "Некорректно введён номер урока по расписанию.\n"
                                  "Введите номер урока по расписанию(1, 2, ...)\n/close - для отмены")
        return 2
    return 3


def get_msg_note_schedule(update, context):
    userid = update.message.chat_id
    note = update.message.text
    if note == '/close':
        send_msg_with_parse_mode(context, userid, "Создание примечания отменено")
        return ConversationHandler.END
    day = context.user_data.get('day', False)
    num_of_lesson = context.user_data.get('num_of_lesson', False)
    if not day or not num_of_lesson:
        send_msg_with_parse_mode(context, userid, "Произошла ошибка при создание примечания")
        return ConversationHandler.END

    database.sql_commands.add_note_schedule(userid, day, num_of_lesson, note)

    send_msg_with_parse_mode(context, userid, "Примечание успешно добавлено")
    return ConversationHandler.END


def delete_schedule_note(update, context):
    userid = str(update.message.chat_id)
    blacklist = database.sql_commands.get_users_of_blacklist()
    if userid in blacklist:
        print(f"\033[94m{datetime.datetime.now()}\033[0m", end=' ')
        print(userid, update.message.text)
        return ConversationHandler.END
    print(f"\033[93m{datetime.datetime.now()}\033[0m")
    print("DEL_NOTE " + str(userid))
    send_msg_with_parse_mode(context, userid, "Удаление примечания\nВведите номер дня недели(1, 2, ...)\n/close - для отмены")
    return 1


def get_day_del_note_schedule(update, context):
    userid = update.message.chat_id
    day = update.message.text
    if day == '/close':
        send_msg_with_parse_mode(context, userid, "Удаление примечания отменено")
        return ConversationHandler.END
    try:
        day = int(day)
        if not (1 <= day <= 7):
            raise ValueError
        context.user_data['day'] = day
        send_msg_with_parse_mode(context, userid, "Введите номер урока по расписанию(1, 2, ...)\n/close - для отмены")
    except ValueError:
        send_msg_with_parse_mode(context, userid, "Некорректно введён день.\nВведите номер дня недели(1, 2, ...)\n/close - для отмены")
        return 1
    return 2


def get_num_of_lesson_del_note_schedule(update, context):
    userid = update.message.chat_id
    num_of_lesson = update.message.text
    if num_of_lesson == '/close':
        send_msg_with_parse_mode(context, userid, "Удаление примечания отменено")
        return ConversationHandler.END
    try:
        num_of_lesson = int(num_of_lesson)
        if not (1 <= num_of_lesson <= 10):
            raise ValueError
        context.user_data['num_of_lesson'] = num_of_lesson
        day = context.user_data.get('day', False)
    except ValueError:
        send_msg_with_parse_mode(context, userid, "Некорректно введён номер урока по расписанию.\n"
                                  "Введите номер урока по расписанию(1, 2, ...)\n/close - для отмены")
        return 2

    if not day or not num_of_lesson:
        send_msg_with_parse_mode(context, userid, "Произошла ошибка при удалении примечания")
        return ConversationHandler.END

    database.sql_commands.delete_note_schedule(userid, day, num_of_lesson)

    send_msg_with_parse_mode(context, userid, "Примечание успешно удалено")
    return ConversationHandler.END
