import datetime
import inspect
import sqlite3
import time

from telegram import ParseMode
from telegram.ext import ConversationHandler

from homework import get_all_homework


def get_schedule(userid: str) -> str or bool:
    sp: dict = get_all_homework(userid, delta=7)
    if type(sp) != dict:
        return False
    day_week = {"__*_Понедельник_*__": 1,
                "__*_Вторник_*__": 2,
                "__*_Среда_*__": 3,
                "__*_Четверг_*__": 4,
                "__*_Пятница_*__": 5,
                "__*_Суббота_*__": 6,
                "__*_Воскресенье_*__": 7}
    dictionary = {}
    notes = get_schedule_notes(userid)
    for key in sp:
        day = key.split()[0]
        for i in range(len(sp[key])):
            try:
                sp[key][i] = ' '.join(sp[key][i][:-1]) + '\n' + notes[day_week[day]][sp[key].index(sp[key][i]) + 1]
            except KeyError:
                sp[key][i] = ' '.join(sp[key][i][:-1])
        dictionary[day] = ['\n'.join(sp[key])]
        # dictionary[day] = ['\n'.join(list(map(lambda x: ' '.join(x[:-1]), sp[key])))]
    dictionary = dict(sorted(dictionary.items(), key=lambda x: day_week[x[0]]))

    send = []
    for key in dictionary:
        send += [key + '\n' + dictionary[key][0]]
    return "\n\n".join(send)


def print_schedule(update, context):
    userid = update.message.chat_id
    print(f"\033[93m{datetime.datetime.now()}\033[0m")
    print("PRINT_SCHEDULE " + str(userid))
    text = get_schedule(userid)
    if not text:
        send_msg(context, userid, 'Произошла ошибка')
        return
    send_msg(context, userid, text)


def add_note_to_schedule(update, context):
    userid = update.message.chat_id
    print(f"\033[93m{datetime.datetime.now()}\033[0m")
    print("ADD_NOTE " + str(userid))
    send_msg(context, userid, "Создание примечания\nВведите номер дня недели(1, 2, ...)\n/close - для отмены")
    return 1


def get_day_add_note_schedule(update, context):
    userid = update.message.chat_id
    day = update.message.text
    if day == '/close':
        send_msg(context, userid, "Создание примечания отменено")
        return ConversationHandler.END
    try:
        day = int(day)
        if not (1 <= day <= 7):
            raise ValueError
        context.user_data['day'] = day
        send_msg(context, userid, "Введите номер урока по расписанию(1, 2, ...)\n/close - для отмены")
    except ValueError:
        send_msg(context, userid, "Некорректно введён день.\nВведите номер дня недели(1, 2, ...)\n/close - для отмены")
        return 1
    return 2


def get_num_of_lesson_add_note_schedule(update, context):
    userid = update.message.chat_id
    num_of_lesson = update.message.text
    if num_of_lesson == '/close':
        send_msg(context, userid, "Создание примечания отменено")
        return ConversationHandler.END
    try:
        num_of_lesson = int(num_of_lesson)
        if not (1 <= num_of_lesson):
            raise ValueError
        context.user_data['num_of_lesson'] = num_of_lesson
        day = context.user_data.get('day', False)
        day_week = {1: "Понедельник", 2: "Вторник", 3: "Среда", 4: "Четверг", 5: "Пятница", 6: "Суббота",
                    7: "Воскресенье"}
        send_msg(context, userid, f"Введите примечание к {num_of_lesson} уроку в {day_week[day]}\n/close - для отмены")
    except ValueError:
        send_msg(context, userid, "Некорректно введён номер урока по расписанию.\n"
                                  "Введите номер урока по расписанию(1, 2, ...)\n/close - для отмены")
        return 2
    return 3


def get_msg_note_schedule(update, context):
    userid = update.message.chat_id
    note = update.message.text
    if note == '/close':
        send_msg(context, userid, "Создание примечания отменено")
        return ConversationHandler.END
    day = context.user_data.get('day', False)
    num_of_lesson = context.user_data.get('num_of_lesson', False)
    if not day or not num_of_lesson:
        send_msg(context, userid, "Произошла ошибка при создание примечания")
        return ConversationHandler.END

    con = sqlite3.connect("db.db")
    cur = con.cursor()
    result = cur.execute(f"""SELECT * FROM notes_of_lessons
                                            WHERE username = '{userid}' and
                                             day = {day} and
                                              number_lesson={num_of_lesson}""").fetchall()
    if not result:
        cur.execute(f"""INSERT into notes_of_lessons(username, day, number_lesson, note)
                     values('{userid}', '{day}', '{num_of_lesson}', '{note}')""")
    else:
        cur.execute(f"""UPDATE notes_of_lessons
                            set note = '{note}'
                            WHERE username = '{userid}' and
                             day = {day} and
                              number_lesson = {num_of_lesson}""")
    con.commit()
    con.close()

    send_msg(context, userid, "Примечание успешно добавлено")
    return ConversationHandler.END


def delete_schedule_note(update, context):
    userid = update.message.chat_id
    print(f"\033[93m{datetime.datetime.now()}\033[0m")
    print("DEL_NOTE " + str(userid))
    send_msg(context, userid, "Удаление примечания\nВведите номер дня недели(1, 2, ...)\n/close - для отмены")
    return 1


def get_day_del_note_schedule(update, context):
    userid = update.message.chat_id
    day = update.message.text
    if day == '/close':
        send_msg(context, userid, "Удаление примечания отменено")
        return ConversationHandler.END
    try:
        day = int(day)
        if not (1 <= day <= 7):
            raise ValueError
        context.user_data['day'] = day
        send_msg(context, userid, "Введите номер урока по расписанию(1, 2, ...)\n/close - для отмены")
    except ValueError:
        send_msg(context, userid, "Некорректно введён день.\nВведите номер дня недели(1, 2, ...)\n/close - для отмены")
        return 1
    return 2


def get_num_of_lesson_del_note_schedule(update, context):
    userid = update.message.chat_id
    num_of_lesson = update.message.text
    if num_of_lesson == '/close':
        send_msg(context, userid, "Удаление примечания отменено")
        return ConversationHandler.END
    try:
        num_of_lesson = int(num_of_lesson)
        if not (1 <= num_of_lesson <= 10):
            raise ValueError
        context.user_data['num_of_lesson'] = num_of_lesson
        day = context.user_data.get('day', False)
    except ValueError:
        send_msg(context, userid, "Некорректно введён номер урока по расписанию.\n"
                                  "Введите номер урока по расписанию(1, 2, ...)\n/close - для отмены")
        return 2

    if not day or not num_of_lesson:
        send_msg(context, userid, "Произошла ошибка при создание примечания")
        return ConversationHandler.END

    con = sqlite3.connect("db.db")
    cur = con.cursor()
    result = cur.execute(f"""SELECT * FROM notes_of_lessons
                                                WHERE username = '{userid}' and
                                                 day = {day} and number_lesson = {num_of_lesson}""").fetchall()
    if result:
        cur.execute(f"""DELETE from notes_of_lessons
                                WHERE username = '{userid}' and
                                 day = {day} and
                                  number_lesson = {num_of_lesson}""")
    con.commit()
    con.close()
    send_msg(context, userid, "Примечание успешно удалено")
    return ConversationHandler.END


def get_schedule_notes(userid: str) -> dict:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    marks = cur.execute(f"""SELECT day, number_lesson, note FROM notes_of_lessons
                            WHERE username = '{userid}'""").fetchall()
    con.close()
    f = {}
    for i in range(len(marks)):
        note = marks[i]
        if note[0] in f:
            f[note[0]][note[1]] = note[2]
        else:
            f[note[0]] = {note[1]: note[2]}
    return f


def send_msg(context, userid: str, msg: str):
    error = False
    msg = msg.replace('=', '\\=').replace('-', '\\-').replace('(', '\\(').replace(')', '\\)').replace('+', '\\+')
    msg = msg.replace('.', '\\.').replace('!', '\\!')
    # print(f"\033[93m{datetime.datetime.now()}\033[0m")
    print(f"\033[93m{datetime.datetime.now()}\033[0m", end=' ')
    try:
        print(userid)
    except Exception:
        pass
    print([msg])
    sent = False
    while not sent:
        try:
            context.bot.send_message(userid, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
            sent = True
        except Exception as ex:
            func_name = inspect.currentframe().f_back.f_code.co_name
            print(f"\033[91m{datetime.datetime.now()} Error in schedule.py in {func_name}\033[0m"
                  f"\n{ex}\n{userid}\n{[msg]}")
            time.sleep(10)
            error = True
    if error:
        print("Отправлено")
