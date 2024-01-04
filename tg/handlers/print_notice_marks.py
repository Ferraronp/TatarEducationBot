import tg.database.sql_commands
from tg.handlers.support_functions.send_msg import *

from tg.handlers.support_functions.check_response import check_response

jobs = {}


def unset_timer(update, context):
    """Убираем оповещения об оценках"""
    username = str(update.message.chat_id)
    blacklist = tg.database.sql_commands.get_users_of_blacklist()
    if username in blacklist:
        logging.info(f"User in blacklist write message: {username}, {update.message.text}")
        return
    userid = str(update.message.from_user.id)
    remove_job_if_exists(str(username), context)
    text = 'Оповещения выключены'
    send_msg_with_parse_mode(context, userid, text)


def remove_job_if_exists(name, context):
    """Убираем задачу из списка"""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    tg.database.sql_commands.update_column_msg(str(name), 0)
    logging.info(f"User removing timer: {name}")
    return True


def set_timer(update, context):
    """Включение оповещений об оценках"""
    username = str(update.message.from_user.id)
    blacklist = tg.database.sql_commands.get_users_of_blacklist()
    if username in blacklist:
        logging.info(f"User in blacklist write message: {username}, {update.message.text}")
        return
    remove_job_if_exists(
        str(username),
        context
    )
    logging.info(f"User set timer: {username}")
    job = context.job_queue.run_repeating(
        task,
        interval=60 * 3,
        first=1,
        context=username,
        name=username,
        job_kwargs={"max_instances": 50}
    )
    tg.database.sql_commands.update_column_msg(username, 1)
    text = 'Оповещения включены'
    send_msg_with_parse_mode(context, username, text)
    jobs[username] = job


def set_timer_off(dp, chat_id):
    """Включение оповещений после перезапуска бота"""
    context = CallbackContext(dp)
    remove_job_if_exists(
        str(chat_id),
        context
    )
    job = context.job_queue.run_repeating(
        task,
        interval=60 * 3,
        first=5,
        context=chat_id,
        name=str(chat_id),
        job_kwargs={"max_instances": 50, "misfire_grace_time": None}
    )
    jobs[chat_id] = job


def task(context):
    """Выводит оповещение"""
    userid = context.job.context
    marks = get_new_marks(userid)
    if type(marks) is str:
        send_msg_with_parse_mode(context, userid, marks)


def print_marks(update, context):
    """Вывод всех оценок"""
    username = str(update.message.from_user.id)
    blacklist = tg.database.sql_commands.get_users_of_blacklist()
    if username in blacklist:
        logging.info(f"User in blacklist write message: {username}, {update.message.text}")
        return
    logging.info(f"User getting marks: {username}")
    message_id = send_msg(update, 'Собираем информацию...')
    try:
        marks = get_marks(username)
    except Exception:
        update_message(context, message_id, username, text='Произошла ошибка, попробуйте позже')
    else:
        update_message(context, message_id, username, text=marks, parse_mode=ParseMode.MARKDOWN_V2)


def get_marks(username: str) -> str:
    """Формирование списка оценок в читаемый вид. Возращает False, если оценок нет"""
    update_marks(username)
    marks = tg.database.sql_commands.get_marks(username)
    if not marks:
        return 'Оценок нет'
    ret = ''
    for mark in marks:
        ret += str(mark[0]).capitalize()
        if mark[2]:
            ret += ":\n" + str(mark[1]) + "\nСредний балл: " + str(mark[2])
        if mark[3]:
            ret += "\nОценка за четверть(полугодие): " + str(mark[3])
        ret += '\n\n'
    return ret.strip()


def get_new_marks(username: str) -> str | bool:
    """Возращает оценки в читаемом виде. True - нет изменений, False - ошибка"""
    marks = update_marks(username)
    if marks is False:  # Ошибка с получением данных
        return False
    if not marks:  # Нет изменений в оценках
        return True
    ret = get_difference(marks)
    return ret


def update_marks(username: str) -> dict | bool:
    marks = get_marks_of_changed_objects(username)
    if type(marks) is bool:
        return False
    for object_ in marks:
        tg.database.sql_commands.add_marks(username, object_,
                                        ' '.join(marks[object_]['new_marks']),
                                           marks[object_]['new_medium'],
                                           marks[object_]['new_mark_of_quarter'])
    return marks


def get_marks_of_changed_objects(username: str) -> dict | bool:
    """Returns:
    {
        "object":
            {
                "old_marks": [...],
                "new_marks": [...],
                "old_mark_of_quarter": float,
                "new_mark_of_quarter": float,
                "old_medium": float,
                "new_medium": float
            }
    }"""
    user = tg.database.sql_commands.get_login_password(username)
    if not user:
        return False
    login, password = tuple(user)
    url = 'http://127.0.0.1:8000/marks'
    data = {"login": login, "password": password}
    marks_response = grequests.get(url, params=data).send().response
    marks = check_response(marks_response)
    if type(marks) is str:
        logging.warning(f"Server cannot update marks to user: {username}")
        return False

    try:
        url = 'http://127.0.0.1:8000/information'
        data = {"login": login, "password": password}
        information_response = grequests.get(url, params=data).send().response
        info = check_response(information_response)
        if type(info) is str:
            logging.warning(f"Server cannot get users school and class: {username}")
        school, class_, medium = info
        tg.database.sql_commands.update_pupil_in_db(login, school, class_, medium)
    except Exception:
        pass

    dictionary = dict()
    for marks_of_object in marks['objects']:
        object_ = marks_of_object['object']
        f = tg.database.sql_commands.get_marks_by_object(username, object_)
        if not f:  # Нет предмета в БД
            old_marks = []
            old_medium = 0
            old_mark_of_quarter = None
        else:
            old_marks = str(f[0][2]).split()
            old_medium = f[0][3]
            old_mark_of_quarter = f[0][4]
        if (old_marks != marks_of_object['marks'] or
                (old_mark_of_quarter != marks_of_object['mark_of_quarter'] and
                 bool(old_mark_of_quarter) != bool(marks_of_object['mark_of_quarter'])) or
                # В БД значение по умолчанию None, с сайта приходит ""
                not f):  # Если пришёл новый предмет с сайта(нет в БД)
            dictionary[object_] = {
                'old_marks': old_marks,
                'new_marks': marks_of_object['marks'],
                'old_mark_of_quarter': old_mark_of_quarter,
                'new_mark_of_quarter': marks_of_object['mark_of_quarter'],
                'old_medium': old_medium,
                'new_medium': marks_of_object['medium']
            }
    return dictionary


def get_difference(dic: dict) -> str:
    """Словарь, где ключ - предмет, значение - кортеж из старых и кортеж из новых оценок,
    старое значение среднего балла и новое"""
    ret = ''
    for key in dic:
        a = ''.join(dic[key]['old_marks'])
        b = ''.join(dic[key]['new_marks'])
        data = difference_of_marks(a, b)
        ret += key + '\n'
        if data != [[], [], []]:  # Есть изменения в оценках
            # Убираем первую строку(пустую), если ни одну оценку не меняли на другую
            if not "".join(data[0]).strip():
                data = data[1:]
            old_medium = dic[key]['old_medium']
            new_medium = dic[key]['new_medium']
            if old_medium <= new_medium:
                sim = '📈'
            else:
                sim = '📉'
            ret += '```\n' + "\n".join(list(map(lambda x: " ".join(x), data))) + \
                   f'\n```Средний балл: {old_medium}{sim}{new_medium}\n'
        # Изменилась оценка за четверть
        if dic[key]['old_mark_of_quarter'] != dic[key]['new_mark_of_quarter'] and \
                bool(dic[key]['old_mark_of_quarter']) != bool(dic[key]['new_mark_of_quarter']):
            ret += 'Изменение оценки за четверть(полугодие): '
            if not dic[key]['new_mark_of_quarter']:
                ret += f'Убрана {dic[key]["old_mark_of_quarter"]}'
            else:
                if dic[key]['old_mark_of_quarter']:
                    ret += dic[key]['old_mark_of_quarter'] + ' -> '
                else:
                    ret += 'Выставлена '
                ret += dic[key]['new_mark_of_quarter']
            ret += '\n'
        ret += '\n'
    return ret.rstrip()


def difference_of_marks(a: str, b: str) -> list:
    """
    :param a: Старые оценки(типа - '453432')
    :param b: Новые оценки (типа - '45343')
    :return: [[], [], []]
    """
    n = len(a)
    m = len(b)
    f = []
    # Расстояние редактирования двух строк с оценками
    for i in range(n + 1):
        f += [[-1] * (m + 1)]
    for i in range(n + 1):
        f[i][0] = i
    for j in range(m + 1):
        f[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            c = int(a[i - 1] != b[j - 1])
            f[i][j] = min(f[i - 1][j] + 1, f[i][j - 1] + 1, f[i - 1][j - 1] + c)

    ret1 = []
    ret2 = []
    ret3 = []
    i = n
    j = m
    # Обратный проход по расстоянию редактирования двух строк с оценками
    while f[i][j] != 0:
        mn = f[i][j] + 1
        mnst = ''
        if i != 0:
            if mn > f[i - 1][j]:
                mn = f[i - 1][j]
                mnst = 'i'
        if j != 0:
            if mn > f[i][j - 1]:
                mn = f[i][j - 1]
                mnst = 'j'
        if i != 0 and j != 0:
            if mn >= f[i - 1][j - 1]:
                mn = f[i - 1][j - 1]
                mnst = 'ij'
        if 'ij' == mnst:
            i -= 1
            j -= 1
            if mn == f[i + 1][j + 1]:
                ret1 += [' ']
                ret2 += [' ']
                ret3 += [str(a[i])]
            else:
                ret1 += [str(a[i])]
                ret2 += ['⇓']
                ret3 += [str(b[j])]
        elif 'i' == mnst:
            i -= 1
            ret1 += [' ']
            ret2 += ['-']
            ret3 += [str(a[i])]
        elif 'j' == mnst:
            j -= 1
            ret1 += [' ']
            ret2 += ['+']
            ret3 += [str(b[j])]
    ret = [ret1[::-1], ret2[::-1], ret3[::-1]]
    return ret
