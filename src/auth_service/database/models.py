from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base