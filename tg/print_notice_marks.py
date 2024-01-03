from imports.imports import *
from parser.marks import get_new_marks, get_marks
import database.sql_commands
from tg.send_msg import *

jobs = {}


def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()

    database.sql_commands.update_column_msg(str(name), 0)
    print(f"\033[93m{datetime.datetime.now()}\033[0m")
    print("REMOVE_TIMER " + str(name))
    return True


def set_timer(update, context):
    """Добавляем задачу в очередь"""
    userid = str(update.message.from_user.id)
    blacklist = database.sql_commands.get_users_of_blacklist()
    if userid in blacklist:
        print(f"\033[94m{datetime.datetime.now()}\033[0m", end=' ')
        print(userid, update.message.text)
        return
    job_removed = remove_job_if_exists(
        str(userid),
        context
    )
    print(f"\033[93m{datetime.datetime.now()}\033[0m")
    print("SET_TIMER " + str(userid))
    job = context.job_queue.run_repeating(
        task,
        interval=60 * 7,
        first=1,
        context=userid,
        name=userid,
        job_kwargs={"max_instances": 50}
    )
    database.sql_commands.update_column_msg(userid, 1)
    text = 'Оповещения включены'
    send_msg_with_parse_mode(context, userid, text)
    jobs[userid] = job


def set_timer_off(dp, chat_id):
    """Добавляем задачу в очередь"""
    context = CallbackContext(dp)
    job_removed = remove_job_if_exists(
        str(chat_id),
        context
    )
    job = context.job_queue.run_repeating(
        task,
        interval=60 * 7,
        first=5,
        context=chat_id,
        name=str(chat_id),
        job_kwargs={"max_instances": 50}
    )
    jobs[chat_id] = job


def task(context):
    """Выводит оповещение"""
    userid = context.job.context
    marks = get_new_marks(userid)
    if type(marks) is str:
        send_msg_with_parse_mode(context, userid, marks)


def unset_timer(update, context):
    chat_id = str(update.message.chat_id)
    blacklist = database.sql_commands.get_users_of_blacklist()
    if chat_id in blacklist:
        print(f"\033[94m{datetime.datetime.now()}\033[0m", end=' ')
        print(chat_id, update.message.text)
        return
    userid = str(update.message.from_user.id)
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Оповещения выключены'
    send_msg_with_parse_mode(context, userid, text)


def print_marks(update, context):
    userid = str(update.message.from_user.id)
    blacklist = database.sql_commands.get_users_of_blacklist()
    if userid in blacklist:
        print(f"\033[94m{datetime.datetime.now()}\033[0m", end=' ')
        print(userid, update.message.text)
        return
    print(f"\033[93m{datetime.datetime.now()}\033[0m")
    print("PRINT_MARKS " + userid)
    marks = get_marks(userid)
    send_msg_with_parse_mode(context, userid, marks)
