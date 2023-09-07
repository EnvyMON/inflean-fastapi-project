from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:todos@127.0.0.1:3307/todos"
engine = create_engine(DATABASE_URL, echo=True)
SessionFactory = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def get_db():
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()