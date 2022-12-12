from gevent import monkey as curious_george
curious_george.patch_all(thread=True, select=False)
from imports import *


def main():
    token = open('parametrs.txt', mode='r').read()
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    con = sqlite3.connect("db.db")
    cur = con.cursor()
    marks = cur.execute("""SELECT username, login, password, msg FROM users""").fetchall()
    con.close()
    for i in marks:
        if i[3] == 1:
            time.sleep(2)
            set_timer_off(dp, i[0])

    """text_handler = MessageHandler(Filters.text, echo)

    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            1: [MessageHandler(Filters.text, get_login)],
            2: [MessageHandler(Filters.text, get_password)]
        },
        fallbacks=[]
    )
    dp.add_handler(start_handler)

    add_note_schedule_handler = ConversationHandler(
        entry_points=[CommandHandler('addnote', add_note_to_schedule)],

        states={
            1: [MessageHandler(Filters.text, get_day_add_note_schedule)],
            2: [MessageHandler(Filters.text, get_num_of_lesson_add_note_schedule)],
            3: [MessageHandler(Filters.text, get_msg_note_schedule)]
        },
        fallbacks=[]
    )
    dp.add_handler(add_note_schedule_handler)

    delete_note_schedule_handler = ConversationHandler(
        entry_points=[CommandHandler('delnote', delete_schedule_note)],

        states={
            1: [MessageHandler(Filters.text, get_day_del_note_schedule)],
            2: [MessageHandler(Filters.text, get_num_of_lesson_del_note_schedule)]
        },
        fallbacks=[]
    )
    dp.add_handler(delete_note_schedule_handler)

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("marks", print_marks))
    dp.add_handler(CommandHandler("homework", print_homework))
    dp.add_handler(CommandHandler("schedule", print_schedule))

    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset_timer,
                                  pass_chat_data=True)
                   )
    dp.add_handler(CommandHandler("close", close_keyboard))

    print(f"Запущено {datetime.datetime.now()}")
    dp.add_handler(text_handler)"""

    handlers = get_handlers()
    for handler in handlers:
        dp.add_handler(handler)
    dp.add_error_handler(error_handler)

    unsleep_on(dp)

    print(f"Запущено {datetime.datetime.now()}")
    updater.start_polling(timeout=30)
    updater.idle()


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print(f"\033[91m{datetime.datetime.now()} Error in main.py\033[0m")
