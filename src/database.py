# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config

config = Config()
engine = create_engine(config.SQLALCHEMY_DATABASE_URI,echo=True)

Session = sessionmaker(bind=engine)
