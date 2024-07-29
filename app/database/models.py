from sqlalchemy import DateTime, String, func, Integer,  ForeignKey, Enum, ARRAY, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import enum


class Sex(enum.Enum):
    male = 'Мужской'
    female = 'Женский'

class Base(DeclarativeBase):
    
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Games(DeclarativeBase):
    __tablename__='Games'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    gamers: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    roles: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    fols: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    points: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    best_step: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True)
    first_dead: Mapped[int] = mapped_column(Integer, nullable=True)


class Statistics(DeclarativeBase):
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
    sex: Mapped[Sex] = mapped_column(Enum(Sex), nullable=True)
    club: Mapped[str] = mapped_column(String(150), nullable=True)
    birthdate: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    


    
    

    

