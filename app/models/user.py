from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Base, get_db
