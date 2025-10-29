from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.base import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(256), unique=True, nullable=False)
    password = Column(String(512), nullable=False)
    masterSalt = Column(String(24), nullable=False)

    credentials = relationship("Credential", back_populates="owner", cascade="all, delete")
