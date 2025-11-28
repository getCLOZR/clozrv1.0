from app.db import engine, Base
from app import models  # important so SQLAlchemy sees the models


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()