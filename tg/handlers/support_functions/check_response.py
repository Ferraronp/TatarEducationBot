import grequests


def check_response(response) -> str | list | dict:
    if response is None:
        return "Произошла ошибка, попробуйте ещё раз через время"
    if response.status_code == 500:
        return "Произошла ошибка, попробуйте ещё раз через время"
    if response.status_code == 400:
        return "Ошибка при авторизации, попробуйте позже или измените данные(/start)"
    return response.json()
