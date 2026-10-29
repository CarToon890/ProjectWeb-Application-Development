import os
import subprocess
import sys
import unittest

from app.database import get_db_url


class DatabaseSafetyTests(unittest.TestCase):
    def test_postgres_url_uses_installed_psycopg2_driver(self):
        url = get_db_url("postgresql://user:password@db.example:5432/appdb")
        self.assertEqual(url.get_dialect().driver, "psycopg2")

    def test_invalid_database_driver_does_not_use_ephemeral_database(self):
        env = dict(os.environ, DATABASE_URL="missingdriver://localhost/db")
        result = subprocess.run(
            [sys.executable, "-c", "from app.database import engine; print(engine.url)"],
            env=env, capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("fallback.db", result.stdout)


if __name__ == "__main__":
    unittest.main()
