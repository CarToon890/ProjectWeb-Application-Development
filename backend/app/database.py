import os
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

raw_url = os.environ.get(
    "DATABASE_URL",
    "postgresql://appuser:apppassword@db:5432/appdb"
)

# Strip whitespace and potential accidental quotes
DATABASE_URL = raw_url.strip().strip('"').strip("'")

# Normalize old postgres:// URI scheme to postgresql:// if needed
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Serverless-friendly engine options (pool_pre_ping checks connectivity before query)
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)


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

    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        print(f"[Database] SQLModel create_all notice: {e}")


def create_db_and_tables() -> None:
    run_migrations()


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
