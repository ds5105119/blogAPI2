from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.app.open_fiscal.api.dependencies import fiscal_service

router = APIRouter()


@router.post("/data", status_code=status.HTTP_200_OK)
async def get_fiscal_data(data: Annotated[dict, Depends(fiscal_service.get_fiscal)]):
    return data
