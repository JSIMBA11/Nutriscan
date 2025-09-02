from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import os

DB_URL = os.getenv('DATABASE_URL', 'sqlite:///nutriscan.db')
engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    name = Column(String)
    pantry_items = relationship('PantryItem', back_populates='user', cascade='all, delete')

class PantryItem(Base):
    __tablename__ = 'pantry_items'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    quantity = Column(Float, default=1)
    user = relationship('User', back_populates='pantry_items')

class Donation(Base):
    __tablename__ = 'donations'
    id = Column(Integer, primary_key=True)
    user_name = Column(String)
    item = Column(String)
    quantity = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    note = Column(Text)

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)

Base.metadata.create_all(engine)