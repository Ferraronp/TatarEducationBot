from imports.imports import *
import database.sql_commands
import parser.edu_login


def get_marks(username: str) -> str:
    """Формирование списка оценок в читаемый вид. Возращает False, если оценок нет"""
    update_marks(username)
    marks = database.sql_commands.get_marks(username)
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


def get_new_marks(username: str):
    marks = update_marks(username)
    if marks is False:  # Ошибка с получением данных
        return False
    if not marks:  # Нет изменений в оценках
        return True
    ret = get_difference(marks)
    return ret


def update_marks(username: str):
    marks = get_marks_of_changed_objects(username)
    if type(marks) is bool:
        return marks
    for object_ in marks:
        database.sql_commands.add_marks(username, object_,
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
    user = database.sql_commands.get_login_password(username)
    if not user:
        return False
    login, password = tuple(user)
    marks = get_marks_from_site(login, password)
    if not marks:
        database.sql_commands.update_column_can(username, 0)
        return False
    database.sql_commands.update_column_can(username, 1)
    dictionary = dict()
    for marks_of_object in marks['objects']:
        object_ = marks_of_object['object']
        f = database.sql_commands.get_marks_by_object(username, object_)
        if not f:  # Нет предмета в базе данных
            old_marks = []
            old_medium = 0
            old_mark_of_quarter = None
        else:
            old_marks = str(f[0][2]).split()
            old_medium = f[0][3]
            old_mark_of_quarter = f[0][4]
        if (old_marks != marks_of_object['marks'] or
                (old_mark_of_quarter != marks_of_object['mark_of_quarter'] and
                 bool(old_mark_of_quarter) != bool(marks_of_object['mark_of_quarter']))):
            dictionary[object_] = {
                'old_marks': old_marks,
                'new_marks': marks_of_object['marks'],
                'old_mark_of_quarter': old_mark_of_quarter,
                'new_mark_of_quarter': marks_of_object['mark_of_quarter'],
                'old_medium': old_medium,
                'new_medium': marks_of_object['medium']
            }
    return dictionary


def get_marks_from_site(login: str, password: str) -> dict:
    """
    :return:
        {
            "objects":
                [
                    {
                        "object": str
                        "marks": [...],
                        "mark_of_quarter": float,
                        "medium": float
                    },
                    ...
                ]
            "medium_for_rating": float
        }"""
    res = parser.edu_login.check(login, password)
    if not res:
        return dict()
    res = res.get("https://edu.tatar.ru/user/diary/term", timeout=120).text
    res = res.replace('&mdash;', '')
    html = BS(res, 'html.parser')
    count = len(html.select('#content > div.r_block > div > div > div > table > tbody > tr'))

    dictionary = dict()
    dictionary['objects'] = list()
    dictionary['medium_for_rating'] = 0
    for i in range(count):
        marks = html.select(f'#content > div.r_block > div > div > div > table > tbody > tr:nth-child({i + 1}) > td')
        if i == count - 1:
            # Последняя строка таблицы(строка итого: средний балл всех средних баллов)
            dictionary['medium_for_rating'] = str(marks[1]).replace('<td>', '').replace('</td>', '')
            continue
        marks = list(map(str, marks))
        marks = list(map(lambda x: x.replace('<td>', '').replace('</td>', ''), marks))
        marks = list(map(lambda x: x.strip(), marks))
        marks.pop(-2)  # Убираем ссылку на кнопку "просмотр"

        object_ = marks.pop(0)
        object_ = " ".join(object_.split())  # Убираем лишние пробелы между словами

        mark_of_quarter = marks.pop(-1)
        medium = marks.pop(-1)
        marks = list(filter(None, marks))
        dictionary['objects'] += [{
            'object': object_,
            'marks': marks,
            'medium': float(medium) if medium else 0,
            'mark_of_quarter': mark_of_quarter
        }]
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
        if dic[key]['old_mark_of_quarter'] != dic[key]['new_mark_of_quarter'] and\
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
    :param a: Старые оценки(типа - '4534')
    :param b: Новые оценки(типа - '4534')
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
