"""DAG for the Oil & Gas data pipeline."""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "airflow",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
}

with DAG(
    dag_id="oil_gas_pipeline",
    description="Extracts, loads and transforms Oil & Gas production data.",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval="0 6 * * *",
    catchup=False,
    tags=["oil_gas", "etl"],
) as dag:

    extract = BashOperator(
        task_id="extract_data",
        bash_command="cd /opt/airflow/project && python src/ingestion/extract_data.py",
    )

    load_bronze = BashOperator(
        task_id="load_bronze",
        bash_command="cd /opt/airflow/project && python src/warehouse/load_bronze.py",
    )

    transform = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/project/oil_gas_dbt && dbt run --profiles-dir .",
    )

    extract >> load_bronze >> transform