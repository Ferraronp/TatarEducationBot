from imports.imports import *
from tg.send_msg import *
import parser.rating
import database.sql_commands


def print_rating(update, context):
    userid = str(update.message.from_user.id)
    blacklist = database.sql_commands.get_users_of_blacklist()
    if userid in blacklist:
        print(f"\033[94m{datetime.datetime.now()}\033[0m", end=' ')
        print(userid, update.message.text)
        return
    print(f"\033[93m{datetime.datetime.now()}\033[0m")
    print("PRINT_RATING " + userid)

    can = database.sql_commands.get_column_can(userid)

    if can:
        msg = parser.rating.get_rating(userid)
    else:
        msg = 'ERROR'
    send_msg_with_parse_mode(context, userid, msg)

