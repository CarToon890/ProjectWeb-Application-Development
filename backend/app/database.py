import os
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://appuser:apppassword@db:5432/appdb"
)

engine = create_engine(DATABASE_URL, echo=False)


def run_migrations() -> None:
    """Run Alembic migrations to head, or fallback to SQLModel.metadata.create_all."""
    try:
        from alembic import command
        from alembic.config import Config

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ini_path = os.path.join(base_dir, "alembic.ini")
        if os.path.exists(ini_path):
            alembic_cfg = Config(ini_path)
            alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))
            command.upgrade(alembic_cfg, "head")
            return
    except Exception as e:
        print(f"[Alembic] Migration notice: {e}, using SQLModel metadata fallback.")

    SQLModel.metadata.create_all(engine)


def create_db_and_tables() -> None:
    run_migrations()


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
