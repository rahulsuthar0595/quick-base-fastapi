from contextlib import contextmanager


@contextmanager
def SQLAlchemyUnitOfWork(session):      # noqa
    db = session()
    try:
        yield db
    finally:
        db.close()
