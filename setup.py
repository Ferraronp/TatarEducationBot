from imports import *


def sql_setup(dp):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    marks = cur.execute("""SELECT username, login, password, msg FROM users
                            WHERE msg = 1""").fetchall()
    con.close()
    for i in marks:
        if i[3] == 1:
            time.sleep(1)
            set_timer_off(dp, i[0])


def init_handlers(dp):
    handlers = get_handlers()
    for handler in handlers:
        dp.add_handler(handler)
    dp.add_error_handler(error_handler)


def setup() -> None:
    token = open('parametrs.txt', mode='r').read()
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    sql_setup(dp)
    init_list_of_ratings()
    update_all_ratings()
    init_handlers(dp)
    unsleep_on(dp)

    print(f"Запущено {datetime.datetime.now()}")
    updater.start_polling(timeout=30)
    updater.idle()
