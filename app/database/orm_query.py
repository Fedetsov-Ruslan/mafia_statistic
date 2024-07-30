from sqlalchemy import exists, select, update, delete, values
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Users, Games, Statistics

async def orm_add_user(session: AsyncSession, data: dict):
    obj = Users(nickname=data['nickname'], gender=data['gender'], club=data['club'])
    
    session.add(obj)
    await session.commit()

async def orm_get_all_users(session: AsyncSession):
    result = await session.execute(select(Users))

    return result.scalars().all()

async def orm_get_all_nicknames(session: AsyncSession):
    result = await session.execute(select(Users.nickname))

    return result.scalars().all()