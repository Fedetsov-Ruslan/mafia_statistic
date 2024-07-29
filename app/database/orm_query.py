from sqlalchemy import exists, select, update, delete, values
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Users, Games, Statistics

async def orm_add_user(session: AsyncSession, data: dict):
    obj = Users(**data)
    
    session.add(obj)
    await session.commit()

