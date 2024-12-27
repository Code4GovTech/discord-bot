import os

# from discord import Member
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.pool import NullPool

load_dotenv(".env")


def get_postgres_uri():
    DB_HOST = os.getenv('POSTGRES_DB_HOST')
    DB_NAME = os.getenv('POSTGRES_DB_NAME')
    DB_USER = os.getenv('POSTGRES_DB_USER')
    DB_PASS = os.getenv('POSTGRES_DB_PASS')

    # DB_URL = os.getenv('DATABASE_URL')
    # print('db')
    return f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'

    
class PostgresORM:
    
    def __init__(self):
        DATABASE_URL = get_postgres_uri()         
        # Initialize Async SQLAlchemy
        engine = create_async_engine(DATABASE_URL, echo=False,poolclass=NullPool)
        async_session = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
        self.session = async_session
        
    def get_instance():
        return PostgresORM()