import sqlite3
from edu_login import check


def get_marks(userid: str) -> str or bool:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    user = cur.execute(f"""SELECT login, password FROM users
        WHERE username = '{userid}'""").fetchone()
    update_marks(userid, user[0], user[1])
    marks = cur.execute(f"""SELECT * FROM marks
                WHERE username = '{userid}'""").fetchall()
    con.close()
    if not marks:
        return False
    marks = list(map(lambda x: str(x[1]).capitalize() + (":\n" + str(x[2]) + "\n" + str(x[3])) * int(x[3] != 0), marks))
    return "\n\n".join(marks)


def get_new_marks(userid: str):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    t = cur.execute(f"""SELECT login, password FROM users
                    WHERE username = '{userid}'""").fetchone()
    con.close()
    if t is None:
        return "Вы не авторизованы\nВведите /start"
    login, password = tuple(t)
    marks = update_marks(userid, login, password)
    if marks is True:
        return True
    if marks is False:
        return False
    ret = get_difference(marks)
    return ret


def update_marks(username, login, password) -> dict or bool:
    """Возвращает True, если нет изменений, иначе
    словарь, где ключ - предмет, значение - кортеж из старых и новых оценок.\n
    Вносит изменения в базу данных оценок"""
    res = check(login, password)
    if not res:
        con = sqlite3.connect("db.db")
        cur = con.cursor()
        cur.execute(f"""UPDATE users
                    set can = 0
                    WHERE username = '{username}'""")
        con.commit()
        con.close()
        return False
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute(f"""UPDATE users
            set can = 1
            WHERE username = '{username}'""")
    con.commit()

    res = "".join("".join("".join(" ".join("".join("".join(res.split("\t")).split('<td>')
                                                   ).split('</td>')).split("<!--")).split("-->")).split(
        "</tr>"))
    res = " ".join(" ".join(res.split("\n")).split())
    res = res.split("<tr>")
    try:
        del res[0]
    except Exception as ex:
        print(ex, 'marks.py(1)')
        print(res)
    try:
        del res[-1]
    except Exception as ex:
        print(ex, 'marks.py(2)')
        print(res)
    res = res[1:]
    res = list(map(lambda x: " ".join(x.split("FIX")[0].split()), res))
    updates = {}
    for i in range(len(res)):
        g = res[i].split()
        j = 0
        while j < len(g) - 1 and g[j] not in list("12345"):
            j += 1
        try:
            sr = float(g[-1])
        except ValueError:
            sr = 0
        object = " ".join(g[:j])
        if sr == 0:
            object = " ".join(g)
        marks = " ".join(g[j:-1])
        result = cur.execute("""SELECT * FROM marks
                                WHERE username = '{}' and object = '{}'""".format(username, object)).fetchall()
        try:
            sr_past = result[0][3]
        except IndexError:
            sr_past = float(0)
        if not result:
            cur.execute("""INSERT into marks(username, object, marks, medium)
                 values('{}', '{}', '{}', {})""".format(username, object, marks, sr))
        else:
            cur.execute("""UPDATE marks
                        set marks = '{}', medium = {}
                        WHERE username = '{}' and object = '{}'""".format(marks, sr, username, object))
        try:
            if str(result[0][2]) != marks:
                updates[object] = (str(result[0][2]), marks, sr_past, sr)
        except IndexError:
            updates[object] = ('', marks, sr_past, sr)
    con.commit()
    con.close()
    if not updates:
        return True
    return updates


def get_difference(dic: dict):
    """Словарь, где ключ - предмет, значение - кортеж из старых и кортеж из новых оценок,
    старое значение среднего балла и новое"""
    ret = ''
    for key in dic:
        a = ''.join(dic[key][0].split())
        b = ''.join(dic[key][1].split())
        data = difference_of_marks(a, b)
        if data != [[], [], []]:
            if not "".join(data[0]).strip():
                data = data[1:]
            sr_past = dic[key][2]
            sr = dic[key][3]
            if sr_past <= sr:
                sim = '📈'
            else:
                sim = '📉'
            ret += key + '\n```\n' + "\n".join(list(map(lambda x: " ".join(x), data))) + \
                   f'\n```Средний балл: {sr_past}{sim}{sr}\n\n'
        else:
            ret += key + '\n'
        # ret += key + '\n' + " ".join(data) + '\n'
    ret = ret  # .replace('(', '\\(').replace(')', '\\)')
    # ret = "```" + ret[:-1] + "```"
    return ret.rstrip()


def difference_of_marks(a: str, b: str) -> list:
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
    ret = []
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
                ret += [str(a[i])]
                ret1 += [' ']
                ret2 += [' ']
                ret3 += [str(a[i])]
            else:
                ret += [f'{str(a[i])} -> {str(b[j])}']
                ret1 += [str(a[i])]
                ret2 += ['⇓']
                ret3 += [str(b[j])]
        elif 'i' == mnst:
            i -= 1
            ret += [f'-{str(a[i])}']
            ret1 += [' ']
            ret2 += ['-']
            ret3 += [str(a[i])]
        elif 'j' == mnst:
            j -= 1
            ret += [f'+{str(b[j])}']
            ret1 += [' ']
            ret2 += ['+']
            ret3 += [str(b[j])]
    ret = [ret1[::-1], ret2[::-1], ret3[::-1]]
    return ret
