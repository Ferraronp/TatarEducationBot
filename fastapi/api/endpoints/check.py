from .. import edu_login
from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def checking_correctness_of_data(login: str, password: str):
    """
        If correct data - status 200, if incorrect - 400
    """
    edu_login.update_cookie(login, password)
    return
