---
status: Accepted
date: 13/06/2026
decision-makers: Isidro Valeriano
consulted: Florencia Zoffi, María Belén Depalo
informed: none
---

# Orchestration Tool for the Oil & Gas Data Pipeline

## Context and Problem Statement

The data pipeline requires coordinating sequential steps: extracting raw data,
loading it into postgreSQL bronze layer, running dbt transformations to build
silver and gold layers, running dbt tests, and persisting quality results.
These steps need to run automatically on a schedule, handle failures with
retries, and provide observability into execution state and logs.

## Decision Drivers

* The pipeline has sequential dependencies between tasks that must be enforced
* The adenda requires idempotency, retries with backoff, and minimum observability
* The tool must support DAGs defined as code
* The solution must integrate with the existing docker-based infrastructure

## Considered Options

* Apache Airflow
* Prefect
* Manual execution via cron jobs

## Decision Outcome

Chosen option: "Apache Airflow", because it is the most widely adopted orchestration
tool in the data engineering industry, supports DAGs defined as code in Python,
provides a built-in web UI for observability, and has native support for retries
with backoff exponential.

### Consequences

* Good, because the pipeline runs automatically every day at 6am UTC (3am in UTC-3, Argentinian time use)
* Good, because each task has 3 automatic retries with backoff
* Good, because the Airflow UI provides full observability of task states and logs
* Good, because DAGs are version controlled in the repository
* Bad, because Airflow is resource-heavy and required upgrading the EC2 instance
  from t2.micro to t3.xlarge to run stably alongside the other services
* Bad, because dependency management between Airflow and dbt required a separate
  virtual environment to avoid conflicts

### Confirmation

The DAG oil_gas_pipeline is deployed and accessible at the Airflow UI on port 8090.
Five tasks run sequentially: extract_data, load_bronze, dbt_run, dbt_test and
persist_quality_result.

## Pros and Cons of the Options

### Apache Airflow

* Good, because it is battle-tested in production data engineering environments
* Good, because it provides a rich web UI for monitoring and manual triggering
* Good, because it supports complex dependency graphs, retries and backoff natively
* Neutral, because it requires PostgreSQL as its metadata database, which we already had
* Bad, because it is resource-intensive, requiring significant RAM to run stably

### Prefect

* Good, because it is more lightweight than Airflow and easier to set up
* Good, because it has a modern Python-native API
* Bad, because the free tier has limitations and self-hosted setup is more complex
* Bad, because we had no prior experience with it

### Manual execution via cron jobs

* Good, because it is the simplest possible solution with no additional infrastructure
* Bad, because it provides no visibility into task state or failure
* Bad, because retry logic would need to be implemented manually

## More Information

The DAG is defined in dags/oil_gas_pipeline.py and runs on a daily schedule at
06:00 UTC. dbt runs inside a dedicated virtual environment at /home/airflow/dbt-env
to avoid dependency conflicts with Airflow's own packages.