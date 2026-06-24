# scripts/test_sql_connection.py
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text
from config.config import (
    SQL_SERVER,
    SQL_DATABASE,
    SQL_DRIVER,
    get_sqlalchemy_engine
)

print(f"SQL_SERVER   = {SQL_SERVER}")
print(f"SQL_DATABASE = {SQL_DATABASE}")
print(f"SQL_DRIVER   = {SQL_DRIVER}")
print("\nAttempting SQL Server connection using Windows Authentication...")

try:
    engine = get_sqlalchemy_engine()

    with engine.connect() as conn:
        result = conn.execute(text("SELECT @@SERVERNAME AS ServerName, DB_NAME() AS DatabaseName"))
        row = result.fetchone()

    print("\nSUCCESS - SQL connection established.")
    print(f"Connected Server   : {row.ServerName}")
    print(f"Connected Database : {row.DatabaseName}")

except Exception as e:
    print("\nFAILED - SQL connection error:")
    print(str(e))
    raise