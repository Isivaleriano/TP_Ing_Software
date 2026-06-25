from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
import uuid
from datetime import datetime, timezone


DB_URL = "postgresql+psycopg2://oilgas:oilgas@oilgas_postgres:5432/oilgas"

ROOT_DIR = Path(__file__).resolve().parents[2]

BRONZE_FILES = {
    "listed_wells": ROOT_DIR / "data" / "bronze" / "listed_wells.csv",
    "wells_production": ROOT_DIR / "data" / "bronze" / "wells_production.csv",
}


def load_csv_to_postgres(engine, table_name: str, csv_path: Path) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(f"File not found: {csv_path}")

    df = pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
        low_memory=False,
        )
    
    run_id = str(uuid.uuid4())
    
    df["load_time"] = datetime.now(timezone.utc)
    df["source_file"] = csv_path.name
    df["run_id"] = run_id

    with engine.begin() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS bronze"))

    df.to_sql(
        name=table_name,
        con=engine,
        schema="bronze",
        if_exists="replace",
        index=False,
    )

    print(f"Loaded bronze.{table_name}: {len(df)} rows")


def main() -> None:
    engine = create_engine(DB_URL)

    for table_name, csv_path in BRONZE_FILES.items():
        load_csv_to_postgres(engine, table_name, csv_path)


if __name__ == "__main__":
    main()