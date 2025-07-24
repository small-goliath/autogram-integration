from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI 의존성용
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def get_db_session_context() -> Session:
    """
    데이터베이스 세션을 제공하는 컨텍스트 관리자로, 항상 세션이 닫히도록 보장합니다.
    백그라운드 작업에 유용합니다.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def with_session(func):
    """
    데코레이터로, 함수에 데이터베이스 세션을 제공합니다.
    함수의 첫 번째 인자로 세션 객체를 전달합니다.
    """
    def wrapper(*args, **kwargs):
        with get_db_session_context() as session:
            return func(session, *args, **kwargs)
    return wrapper


@contextmanager
def transaction_scope(session: Session):
    """
    특정 코드 블록에 대한 트랜잭션 범위를 제공하는 컨텍스트 관리자입니다.
    블록이 성공적으로 완료되면 커밋하고, 예외 발생 시 롤백합니다.
    세션을 직접 닫지는 않습니다.
    """
    try:
        yield
        session.commit()
    except Exception:
        session.rollback()
        raise

@contextmanager
def read_only_transaction_scope(session: Session):
    """
    특정 코드 블록에 대한 트랜잭션 범위를 제공하는 컨텍스트 관리자입니다.
    블록이 성공적으로 완료되면 커밋하고, 예외 발생 시 롤백합니다.
    세션을 직접 닫지는 않습니다.
    """
    try:
        yield
    except Exception:
        session.rollback()
        raise
