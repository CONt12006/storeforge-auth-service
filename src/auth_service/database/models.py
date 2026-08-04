from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement=True)


class rolls(Base):
    pass 

class user_roles(Base):
    pass