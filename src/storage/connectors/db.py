from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class DatabaseManager(metaclass=SingletonMeta):
    def __init__(self):
        load_dotenv()
        self.engine = create_engine(os.getenv("DATABASE_URL"))
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        self.Base = declarative_base()

    def get_session(self):
        return self.SessionLocal()