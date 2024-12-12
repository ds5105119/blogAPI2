from typing import Annotated

from fastapi import APIRouter, Depends, status
from webtool.throttle import limiter

from src.app.open_fiscal.api.dependencies import fiscal_service

router = APIRouter()


@limiter(max_requests=10000)
@router.get("/data", status_code=status.HTTP_200_OK)
async def get_fiscal_data(data: Annotated[list, Depends(fiscal_service.get_fiscal)]):
    return data
