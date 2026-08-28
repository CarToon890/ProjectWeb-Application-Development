import os
import urllib.parse
from collections.abc import Generator

from sqlalchemy.engine import URL
from sqlmodel import Session, SQLModel, create_engine


def get_db_url(raw_url: str):
    """Parse and convert raw connection string into a safe SQLAlchemy URL object or string."""
    if not raw_url:
        return "postgresql://appuser:apppassword@db:5432/appdb"

    clean_url = raw_url.strip().strip('"').strip("'")
    if clean_url.startswith("postgres://"):
        clean_url = clean_url.replace("postgres://", "postgresql://", 1)

    try:
        if "://" in clean_url and "@" in clean_url:
            driver, rest = clean_url.split("://", 1)
            auth_part, host_part = rest.rsplit("@", 1)

            if ":" in auth_part:
                user, pwd = auth_part.split(":", 1)
            else:
                user, pwd = auth_part, None

            if "/" in host_part:
                host_port, dbname = host_part.split("/", 1)
            else:
                host_port, dbname = host_part, "postgres"

            if "?" in dbname:
                dbname, _ = dbname.split("?", 1)

            if ":" in host_port:
                host, port_str = host_port.split(":", 1)
                try:
                    port = int(port_str)
                except ValueError:
                    port = 5432
            else:
                host, port = host_port, 5432

            return URL.create(
                drivername=driver or "postgresql",
                username=urllib.parse.unquote(user) if user else None,
                password=urllib.parse.unquote(pwd) if pwd else None,
                host=host,
                port=port,
                database=dbname or "postgres",
            )
    except Exception as e:
        print(f"[DB URL Parser Notice] Using raw url fallback: {e}")

    return clean_url


RAW_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://appuser:apppassword@db:5432/appdb"
)

DATABASE_URL = get_db_url(RAW_DATABASE_URL)

try:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
    )
except Exception as e:
    print(f"[Engine Creation Notice] Primary engine error ({e}), falling back...")
    engine = create_engine(
        "sqlite:////tmp/fallback.db",
        echo=False,
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
