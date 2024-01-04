from .. import edu_login
from bs4 import BeautifulSoup as BS
from fastapi import APIRouter


router = APIRouter()


@router.get("/")
def get_marks_from_site(login: str, password: str) -> dict:
    """
        {\n
            "objects":\n
                [\n
                    {\n
                        "object": str\n
                        "marks": [...],\n
                        "mark_of_quarter": float,\n
                        "medium": float\n
                    },\n
                    ...\n
                ]\n
            "medium_for_rating": float\n
        }
    """
    res = edu_login.get_url(login, password, "https://edu.tatar.ru/user/diary/term")
    html = BS(res, 'html.parser')
    count = len(html.select('#content > div.r_block > div > div > div > table > tbody > tr'))

    dictionary = dict()
    dictionary['objects'] = list()
    dictionary['medium_for_rating'] = 0
    for i in range(1, count + 1):
        marks = html.select(f'#content > div.r_block > div > div > div > table > tbody > tr:nth-child({i}) > td')
        if i == count:
            # Последняя строка таблицы(строка итого: средний балл всех средних баллов)
            dictionary['medium_for_rating'] = marks[1].getText()
            continue
        marks = list(map(lambda x: x.getText(), marks))
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
