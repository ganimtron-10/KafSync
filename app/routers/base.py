from fastapi import APIRouter
from . import customer

router = APIRouter(
    prefix='/api/v1'
)

router.include_router(customer.router)
