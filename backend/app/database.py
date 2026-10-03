import os
import urllib.parse
from collections.abc import Generator

from sqlalchemy.engine import URL
from sqlmodel import Session, SQLModel, create_engine


def get_db_url(raw_url: str):
    """Parse and convert raw connection string into a safe SQLAlchemy URL object or string."""
    if not raw_url:
        return "postgresql://appuser:apppassword@db:5432/appdb"

    clean_url = raw_url.strip()
    # Strip any prefix like DATABASE_URL= or export DATABASE_URL=
    if clean_url.startswith("export "):
        clean_url = clean_url[7:].strip()
    if clean_url.startswith("DATABASE_URL="):
        clean_url = clean_url[len("DATABASE_URL="):].strip()
    elif clean_url.startswith("DATABASE_URL ="):
        clean_url = clean_url.split("=", 1)[1].strip()

    # Strip surrounding quotes
    clean_url = clean_url.strip().strip('"').strip("'")

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

            query_dict = {}
            if "?" in dbname:
                dbname, query_str = dbname.split("?", 1)
                for q in query_str.split("&"):
                    if "=" in q:
                        qk, qv = q.split("=", 1)
                        # psycopg2 rejects 'pgbouncer' and 'connection_limit' (these are Prisma specific)
                        if qk.lower() not in ("pgbouncer", "connection_limit"):
                            query_dict[qk] = qv

            # Ensure sslmode for Supabase if not specified
            if "pooler.supabase.com" in host or "supabase.co" in host:
                query_dict.setdefault("sslmode", "require")


            if ":" in host_port:
                host, port_str = host_port.split(":", 1)
                try:
                    port = int(port_str)
                except ValueError:
                    port = 5432
            else:
                host, port = host_port, 5432

            return URL.create(
                drivername="postgresql",
                username=urllib.parse.unquote(user) if user else None,
                password=urllib.parse.unquote(pwd) if pwd else None,
                host=host,
                port=port,
                database=dbname or "postgres",
                query=query_dict if query_dict else None,
            )
    except Exception as e:
        print(f"[DB URL Parser Notice] Using raw url fallback: {e}")

    return clean_url



RAW_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://appuser:apppassword@db:5432/appdb"
)

DATABASE_URL = get_db_url(RAW_DATABASE_URL)

ENGINE_ERROR = None

try:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
    )
except Exception as e:
    ENGINE_ERROR = str(e)
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
