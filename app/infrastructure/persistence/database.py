from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine as sqlalchemy_create_engine
from sqlalchemy.orm import Session, sessionmaker

def create_engine(database_url: str, **kwargs: object):
    """Create the application engine; SQLite URLs are useful for local tests."""
    return sqlalchemy_create_engine(database_url, pool_pre_ping=True, **kwargs)


def create_session_factory(engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@contextmanager
def session_scope(factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    """Commit a unit of work and roll it back if persistence fails."""
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
