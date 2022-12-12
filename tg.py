import datetime
import time

from telegram import ReplyKeyboardRemove
from telegram.ext import Filters, MessageHandler, CommandHandler, PrefixHandler

from edu_login import *
from print_notice_marks import *
from homework import *
from schedule import *


def echo(update, context):
    """reply_keyboard = [['/help', '/close'],
                      ['/start', '/marks'],
                      ['/set', '/unset'],
                      ['/homework', '/schedule'],
                      ['/addnote', '/delnote']]"""

    reply_keyboard = [['/help', '/close'],
                      ['🖋️Изменить логин/пароль', '📊Оценки'],
                      ['⏰✅Вкл. оповещения', '⏰❌Выкл. оповещения'],
                      ['📚Домашние задание', '📖Расписание'],
                      ['📝Создать примечание', '🗑️Удалить примечание']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
    sent = False
    while not sent:
        try:
            update.message.reply_text("/close - закрыть клавиатуру\n" +
                                      "/start - смена логина и пароля\n/marks - вывод всех оценок\n" +
                                      "/set - включить оповещения об оценках\n/unset - отключить уведомления\n" +
                                      "/homework - список домашних заданий на неделю\n/schedule - расписание уроков\n" +
                                      "/addnote - создать примечание к уроку в расписание\n" +
                                      "/delnote - удалить примечание к уроку в расписание",
                                      reply_markup=markup
                                      )
            sent = True
        except Exception as ex:
            print(f"\033[91m{datetime.datetime.now()} Error bot.send_message in tg.py in echo\033[0m\n{ex}")
            time.sleep(10)


def close_keyboard(update, context):
    sent = False
    while not sent:
        try:
            update.message.reply_text(
                "Клавиатура скрыта",
                reply_markup=ReplyKeyboardRemove()
            )
            sent = True
        except Exception as ex:
            print(f"\033[91m{datetime.datetime.now()} Error bot.send_message in tg.py in close_keyboard\033[0m\n{ex}")
            time.sleep(10)


def get_handlers():
    handlers = []

    text_handler = MessageHandler(Filters.text, echo)

    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      PrefixHandler('🖋️', "Изменить", start)],

        states={
            1: [MessageHandler(Filters.text, get_login)],
            2: [MessageHandler(Filters.text, get_password)]
        },
        fallbacks=[]
    )
    handlers += [start_handler]

    add_note_schedule_handler = ConversationHandler(
        entry_points=[CommandHandler('addnote', add_note_to_schedule),
                      PrefixHandler("📝", "Создать", add_note_to_schedule)],

        states={
            1: [MessageHandler(Filters.text, get_day_add_note_schedule)],
            2: [MessageHandler(Filters.text, get_num_of_lesson_add_note_schedule)],
            3: [MessageHandler(Filters.text, get_msg_note_schedule)]
        },
        fallbacks=[]
    )
    handlers += [add_note_schedule_handler]

    delete_note_schedule_handler = ConversationHandler(
        entry_points=[CommandHandler('delnote', delete_schedule_note),
                      PrefixHandler('🗑️', 'Удалить', delete_schedule_note)],

        states={
            1: [MessageHandler(Filters.text, get_day_del_note_schedule)],
            2: [MessageHandler(Filters.text, get_num_of_lesson_del_note_schedule)]
        },
        fallbacks=[]
    )
    handlers += [delete_note_schedule_handler]

    handlers += [
        CommandHandler("marks", print_marks),
        CommandHandler("homework", print_homework),
        CommandHandler("schedule", print_schedule),
        CommandHandler("set", set_timer,
                       pass_args=True,
                       pass_job_queue=True,
                       pass_chat_data=True),
        CommandHandler("unset", unset_timer,
                       pass_chat_data=True),
        CommandHandler("close", close_keyboard)
    ]

    handlers += [
        PrefixHandler('🖋️', "Изменить", start),
        PrefixHandler('📊', 'Оценки', print_marks),
        PrefixHandler('📚', 'Домашние', print_homework),
        PrefixHandler('📖', 'Расписание', print_schedule),
        PrefixHandler("⏰✅", "Вкл.", set_timer,
                      pass_args=True,
                      pass_job_queue=True,
                      pass_chat_data=True),
        PrefixHandler("⏰❌", "Выкл.", unset_timer,
                      pass_chat_data=True)
    ]

    handlers += [text_handler]
    return handlers


def unsleep_on(dp) -> None:
    context = CallbackContext(dp)
    job = context.job_queue.run_repeating(
        unsleep,
        interval=300,
        first=5,
        context=604831762,
        name='604831762'
    )


def unsleep(context) -> None:
    userid = context.job.context
    msg = context.bot.send_message(userid, text='test')
    context.bot.delete_message(msg.chat.id, msg.message_id)
    # print(msg.chat.id, msg.message_id)


def error_handler(update, context):
    print(f"\033[91m{datetime.datetime.now()} Error\033[0m\n{context.error}")
    try:
        print(update.message.from_user.id)
        print(update.message.text)
    except Exception as ex:
        pass
        # print(f"\033[91m{datetime.datetime.now()} Error\033[0m\n{ex}")
