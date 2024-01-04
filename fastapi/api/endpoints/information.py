from .. import edu_login
from bs4 import BeautifulSoup as BS
from fastapi import APIRouter


router = APIRouter()


@router.get("/")
def get_information_about_school_and_class(login: str, password: str) -> tuple[str, str, float]:
    """
    :return: (school: str, class: str, medium: float)
    """

    urls = ['https://edu.tatar.ru/user/anketa/edit', 'https://edu.tatar.ru/user/diary/term']
    texts = edu_login.get_urls(login, password, urls)

    school = texts[0]
    school = school.replace('&mdash;', '')
    html = BS(school, 'html.parser')
    school = html.select(
        'body > div.container > div.row >'
        ' #cabinet > div.col-md-9.col > div > div.panel-body > div > div.col-md-9 > div >'
        ' #frm > table > tr:nth-child(5) > td:nth-child(2)'
    )
    school = school[0].getText().strip()

    marks_class = texts[1]
    marks_class = marks_class.replace('&mdash;', '')
    html = BS(marks_class, 'html.parser')
    class_ = html.select('#content > div.r_block > div > div > p:nth-child(2)')[0].getText()
    class_ = class_.split('Класс: ')[1].strip()

    count = len(html.select('#content > div.r_block > div > div > div > table > tbody > tr'))
    medium = html.select(f'#content > div.r_block > div > div > div > table > tbody > tr:nth-child({count}) > td')
    medium = medium[1].getText()
    try:
        medium = float(medium)
    except ValueError:
        medium = 0.0
    return school, class_, medium
