from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi_pagination.async_paginator import paginate

from src.app.open_fiscal.api.dependencies import fiscal_service
from src.core.utils.polarspagination import LazyFramePage

router = APIRouter()


@router.get("/data", status_code=status.HTTP_200_OK)
async def get_fiscal_data(data: Annotated[dict, Depends(fiscal_service.get_fiscal)]) -> LazyFramePage[dict]:
    return await paginate(data)
