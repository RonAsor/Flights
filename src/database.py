# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI,echo=True)

Session = sessionmaker(bind=engine)
