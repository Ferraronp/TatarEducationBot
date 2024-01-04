from fastapi import APIRouter

from api.endpoints import marks
from api.endpoints import homework
from api.endpoints import check
from api.endpoints import information

api_router = APIRouter()
api_router.include_router(marks.router, prefix="/marks")
api_router.include_router(homework.router, prefix="/homework")
api_router.include_router(check.router, prefix="/check")
api_router.include_router(information.router, prefix='/information')
