from fastapi import APIRouter

router = APIRouter(
    prefix='/customer',
    tags=['customer']
)


@router.get('/')
async def index():
    return {'msg': "Hello world!"}
