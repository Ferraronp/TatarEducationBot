from handlers_points import *
import tg.database.sql_commands as sql_commands


def sql_setup(dp):
    """Включает оповещения у людей, которых они были включены до перезапуска"""
    marks = sql_commands.get_username_password_login_where_msg()
    for i in marks:
        set_timer_off(dp, i[0])


def init_handlers(dp):
    handlers = get_handlers()
    for handler in handlers:
        dp.add_handler(handler)
    dp.add_error_handler(error_handler)
