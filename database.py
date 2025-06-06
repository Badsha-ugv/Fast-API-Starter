from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# database url
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:rootuser@localhost:5432/fastapidb"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # connect_args={
    #     "check_same_thread": False # user this for sqlite onlyl
    # }
)

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Get database session"""
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
