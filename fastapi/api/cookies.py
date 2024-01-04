import sqlite3


def get_cookie_from_db(login: str, password: str) -> tuple | None:
    """
    :param login: логин от edu.tatar.ru
    :param password: пароль от edu.tatar.ru
    :return: (HLP_cookie, DNSID_cookie) or None
    """
    con = sqlite3.connect("api/cookies.db")
    cur = con.cursor()
    result = cur.execute(f"""SELECT DNSID_cookie FROM cookies
                        WHERE login = ? and password = ?""", (login, password)).fetchone()
    con.commit()
    con.close()
    return result


def update_cookie_in_db(login: str, password: str, dnsid_cookie: str) -> None:
    """
    :param login: логин от edu.tatar.ru
    :param password: пароль от edu.tatar.ru
    """
    con = sqlite3.connect("api/cookies.db")
    cur = con.cursor()
    result = cur.execute(f"""SELECT * from cookies
                              WHERE login = ? and password = ?""",
                         (login, password)).fetchone()
    try:
        if result:
            cur.execute(f"""UPDATE cookies
                                  SET DNSID_cookie = ?
                                  WHERE login = ? and password = ?""",
                        (dnsid_cookie, login, password))
        else:
            cur.execute(f"""INSERT INTO cookies(DNSID_cookie, login, password) VALUES(?, ?, ?)""",
                        (dnsid_cookie, login, password))
    except sqlite3.OperationalError or sqlite3.IntegrityError:
        pass
    con.commit()
    con.close()
