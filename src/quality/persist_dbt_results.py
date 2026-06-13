from pathlib import Path
import json

from sqlalchemy import create_engine, text


DB_URL = "postgresql+psycopg2://oilgas:oilgas@oilgas_postgres:5432/oilgas"

ROOT_DIR = Path(__file__).resolve().parents[2]
RUN_RESULTS_PATH = ROOT_DIR / "oil_gas_dbt" / "target" / "run_results.json"


def main() -> None:
    if not RUN_RESULTS_PATH.exists():
        raise FileNotFoundError(f"File not found: {RUN_RESULTS_PATH}")

    data = json.loads(RUN_RESULTS_PATH.read_text())

    invocation_id = data.get("metadata", {}).get("invocation_id")

    rows = []
    for result in data.get("results", []):
        unique_id = result.get("unique_id", "")
        if not unique_id.startswith("test."):
            continue

        rows.append(
            {
                "invocation_id": invocation_id,
                "unique_id": unique_id,
                "test_name": unique_id.split(".")[-1],
                "status": result.get("status"),
                "failures": result.get("failures"),
                "execution_time": result.get("execution_time"),
            }
        )

    engine = create_engine(DB_URL)

    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS quality"))

        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS quality.test_results (
                    id SERIAL PRIMARY KEY,
                    invocation_id TEXT,
                    unique_id TEXT,
                    test_name TEXT,
                    status TEXT,
                    failures INTEGER,
                    execution_time DOUBLE PRECISION,
                    persisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )

        for row in rows:
            conn.execute(
                text(
                    """
                    INSERT INTO quality.test_results (
                        invocation_id,
                        unique_id,
                        test_name,
                        status,
                        failures,
                        execution_time
                    )
                    VALUES (
                        :invocation_id,
                        :unique_id,
                        :test_name,
                        :status,
                        :failures,
                        :execution_time
                    )
                    """
                ),
                row,
            )

    print(f"Persisted {len(rows)} dbt test results")


if __name__ == "__main__":
    main()