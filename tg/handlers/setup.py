import time

import database.sql_commands
from parser.rating import init_list_of_ratings
from tg.handlers.handlers import *


def sql_setup(dp):
    marks = database.sql_commands.get_userid_password_login_where_msg()
    for i in marks:
        time.sleep(1)
        set_timer_off(dp, i[0])


def init_handlers(dp):
    handlers = get_handlers()
    for handler in handlers:
        dp.add_handler(handler)
    dp.add_error_handler(error_handler)


def setup() -> None:
    start_time = time.time()
    token = open('tg/handlers/parametrs.txt', mode='r').read()
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    sql_setup(dp)
    init_list_of_ratings()
    init_handlers(dp)
    unsleep_on(dp)

    print(time.time() - start_time)
    print(f"Запущено {datetime.datetime.now()}")
    updater.start_polling()
    updater.idle()
