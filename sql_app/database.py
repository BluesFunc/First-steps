from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHMEMY_DATABASE_URL = "postgresql://Alex:1234@localhost/FastAPI"

engine = create_engine(
    SQLALCHMEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
