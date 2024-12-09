from typing import Annotated

import polars as pl
from fastapi import APIRouter, Depends, status
from webtool.throttle import limiter

from src.app.open_fiscal.api.dependencies import fiscal_service
from src.core.utils.polarspagination import LazyFramePage, paginate

router = APIRouter()


@limiter(max_requests=1000)
@router.get("/data", status_code=status.HTTP_200_OK)
async def get_fiscal_data(data: Annotated[pl.LazyFrame, Depends(fiscal_service.get_fiscal)]) -> LazyFramePage[dict]:
    return await paginate(data)
