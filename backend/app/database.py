import os
import urllib.parse
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine


def clean_database_url(url: str) -> str:
    """Sanitize and ensure special characters in DB password/user are URL-encoded."""
    if not url:
        return url
    url = url.strip().strip('"').strip("'")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    try:
        if "://" in url and "@" in url:
            scheme, rest = url.split("://", 1)
            # Find the last '@' which separates credentials from host
            last_at_idx = rest.rfind("@")
            if last_at_idx != -1:
                auth_part = rest[:last_at_idx]
                host_part = rest[last_at_idx + 1 :]
                if ":" in auth_part:
                    user, password = auth_part.split(":", 1)
                    # Unquote first to prevent double-encoding, then safely quote
                    safe_user = urllib.parse.quote(urllib.parse.unquote(user), safe="")
                    safe_password = urllib.parse.quote(urllib.parse.unquote(password), safe="")
                    return f"{scheme}://{safe_user}:{safe_password}@{host_part}"
    except Exception as e:
        print(f"[Database URL Parser Notice] Auto-repair skipped: {e}")

    return url


RAW_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://appuser:apppassword@db:5432/appdb"
)

DATABASE_URL = clean_database_url(RAW_URL)

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
