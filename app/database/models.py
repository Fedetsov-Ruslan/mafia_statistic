from sqlalchemy import DateTime,Date, String, func, Integer,  ForeignKey, Enum, ARRAY, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date

import enum

class Base(DeclarativeBase):
    
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Games(Base):
    __tablename__='games'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    types_game: Mapped[str] = mapped_column(String(15), nullable=False)
    date_game: Mapped[date] = mapped_column(Date, nullable=False)
    gamers: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    roles: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    fols: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    points: Mapped[list[float]] = mapped_column(ARRAY(Float), nullable=False)
    best_step: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    first_dead: Mapped[str] = mapped_column(String(150), nullable=True)
    winner: Mapped[str] = mapped_column(String(15), nullable=True)


class Statistics(Base):
    __tablename__='statistics'

    userID: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    reting: Mapped[int] = mapped_column(Integer, nullable=False)
    count_games: Mapped[int] = mapped_column(Integer, nullable=False)
    winrate: Mapped[list[float]] = mapped_column(ARRAY(Float), nullable=False)
    first_dead: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    civilian_vinrate:Mapped[list[float]] = mapped_column(ARRAY(Float), nullable=False)
    mafia_vinrate: Mapped[list[float]] = mapped_column(ARRAY(Float), nullable=False)
    sheriff_vinrate: Mapped[list[float]] = mapped_column(ARRAY(Float), nullable=False)
    don_vinrate: Mapped[list[float]] = mapped_column(ARRAY(Float), nullable=False)
    fols_on_the_game: Mapped[float] = mapped_column(Float, nullable=True)
    

class Users(Base):
    __tablename__='users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nickname: Mapped[str] = mapped_column(String(150), nullable=False)
    gender: Mapped[str] = mapped_column(String(15), nullable=True)
    club: Mapped[str] = mapped_column(String(150), nullable=True)
    # birthdate: Mapped[date] = mapped_column(Date, nullable=True)
    


    
    

    

