import sqlite3
import time
import datetime
import inspect

from telegram import ParseMode
from telegram.ext import CallbackContext
from marks import get_new_marks, get_marks

jobs = {}


def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute(f"""UPDATE users
    set msg = 0
    WHERE username = '{int(name)}'""")
    con.commit()
    con.close()
    return True


def set_timer(update, context):
    """Добавляем задачу в очередь"""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(
        str(chat_id),
        context
    )
    job = context.job_queue.run_repeating(
        task,
        interval=60 * 2,
        first=1,
        context=chat_id,
        name=str(chat_id),
        job_kwargs={"max_instances": 10}
    )
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute("""UPDATE users
                set msg = 1
                WHERE username = '{}'""".format(chat_id))
    con.commit()
    con.close()
    text = 'Оповещения включены'
    # update.message.reply_text(text)
    userid = str(update.message.from_user.id)
    send_msg(context, userid, text)
    jobs[chat_id] = job


def set_timer_off(dp, chat_id):
    """Добавляем задачу в очередь"""
    context = CallbackContext(dp)
    job_removed = remove_job_if_exists(
        str(chat_id),
        context
    )
    job = context.job_queue.run_repeating(
        task,
        interval=60 * 2,
        first=5,
        context=chat_id,
        name=str(chat_id),
        job_kwargs={"max_instances": 10}
    )
    jobs[chat_id] = job


def task(context):
    """Выводит оповещение"""
    userid = context.job.context
    marks = get_new_marks(userid)
    if type(marks) is str:
        # context.bot.send_message(userid, text=marks, parse_mode=ParseMode.MARKDOWN_V2)
        send_msg(context, userid, marks)


def unset_timer(update, context):
    chat_id = update.message.chat_id
    userid = str(update.message.from_user.id)
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Оповещения выключены'
    # update.message.reply_text(text)
    send_msg(context, userid, text)


def print_marks(update, context):
    userid = str(update.message.from_user.id)
    print(f"\033[93m{datetime.datetime.now()}\033[0m")
    print("PRINT_MARKS " + userid)
    marks = get_marks(userid)
    if not marks:
        # update.message.reply_text("Введите /start")
        send_msg(context, userid, "Введите /start")
        return
    # update.message.reply_text("\n\n".join(marks))
    send_msg(context, userid, marks)


def send_msg(context, userid: str, msg: str):
    error = False
    msg = msg.replace('=', '\\=').replace('-', '\\-').replace(".", "\\.")
    msg = msg.replace("(", "\\(").replace(")", "\\)").replace('+', '\\+')
    sent = False
    while not sent:
        try:
            context.bot.send_message(userid, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
            sent = True
        except Exception as ex:
            func_name = inspect.currentframe().f_back.f_code.co_name
            print(f"\033[91m{datetime.datetime.now()} Error bot.send_message in print_notice_marks.py"
                  f" in {func_name}\033[0m"
                  f"\n{ex}\n{userid}\n{[msg]}")
            try:
                if 'blocked' in str(ex):
                    break
            except Exception:
                pass
            time.sleep(10)
            error = True
    if error:
        print("Отправлено")
