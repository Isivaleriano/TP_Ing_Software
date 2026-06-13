# Runbook: Data Engineer

## 1. Purpose and Trigger

### Purpose

This runbook defines the operational procedures required to execute, monitor, validate and recover the Oil & Gas Data Platform.

The Data Engineer is responsible for ensuring pipeline availability, successful execution of transformations, persistence of quality controls and overall platform reliability.

### When to Execute

#### Scheduled Execution

The pipeline is automatically executed every day at 06:00 UTC (3:00 UTC-3, Argentinian time use) through apache airflow.

#### Event

This runbook shall be executed when:

- A new version of the pipeline is deployed.
- New transformations are introduced.
- New data quality validations are implemented.
- Infrastructure components are updated.

#### Incident

This runbook shall be executed when:

- A DAG execution fails.
- A transformation process fails.
- A data quality validation fails.
- PostgreSQL becomes unavailable.
- Airflow becomes unavailable.

#### Request

This runbook shall be executed when:

- Historical data must be reprocessed.
- Data quality results must be validated manually.
- A manual execution of the pipeline is requested.

---

## 2. Role Owner and Prerequisites

### Role Owner

Data Engineer.

### Required Access

The Data Engineer shall have access to:

- Apache airflow web UI.
- PostgreSQL database.
- GitHub repository.
- EC2 instance through SSH.
- Docker environment.

### Required Inputs

The Data Engineer shall have access to:

- The latest version of the source code.
- Airflow credentials.
- PostgreSQL credentials.
- SSH key for EC2 access.

### Required Tools

- Apache airflow.
- PostgreSQL.
- Docker.
- dbt.
- Git.
- SQL client.

---

## 3. Procedures

### 3.1 Daily Pipeline Monitoring

The Data Engineer shall monitor the daily execution of the pipeline through Apache airflow.

The following tasks must complete successfully:

- `extract_data`
- `load_bronze`
- `dbt_run`
- `dbt_test`
- `persist_quality_results`

The Data Engineer shall verify that:

- All tasks finish with status "success".
- No retries are triggered.
- Execution durations remain within expected ranges.

---

### 3.2 Manual Pipeline Execution

When a manual execution is required, the Data Engineer shall trigger the DAG from Airflow.

Procedure:

1. Access the Airflow Web UI.
2. Open the DAG `oil_gas_pipeline`.
3. Trigger a new DAG execution.
4. Monitor task execution until completion.

Alternatively, the DAG may be executed from the EC2 instance:

```bash
docker exec airflow_scheduler \
airflow dags trigger oil_gas_pipeline
```

---

### 3.3 Historical Reprocessing (Backfill)

When historical data needs to be reconstructed, the Data Engineer shall execute a backfill operation.

Procedure:

```bash
docker exec airflow_scheduler \
airflow dags backfill oil_gas_pipeline \
--start-date YYYY-MM-DD \
--end-date YYYY-MM-DD
```

The Data Engineer shall monitor execution progress through Airflow and verify successful completion of all generated runs.

---

### 3.4 Transformation Validation

The Data Engineer shall verify successful execution of the `dbt_run` task.

If manual execution is required:

```bash
docker exec -it airflow_scheduler bash

cd /opt/airflow/project/oil_gas_dbt

/home/airflow/dbt-env/bin/dbt deps --profiles-dir .

/home/airflow/dbt-env/bin/dbt run \
--profiles-dir . \
--no-use-colors
```

The Data Engineer shall confirm that all models are built successfully.

---

### 3.5 Data Quality Validation

The Data Engineer shall verify successful execution of the `dbt_test` task.

If manual validation is required:

```bash
docker exec -it airflow_scheduler bash

cd /opt/airflow/project/oil_gas_dbt

/home/airflow/dbt-env/bin/dbt test \
--profiles-dir . \
--no-use-colors
```

The Data Engineer shall review any failing tests and determine the root cause before re-executing the pipeline.

---

### 3.6 Quality Results Persistence Validation

The Data Engineer shall verify successful execution of the `persist_quality_results` task.

The Data Engineer shall confirm that quality validation results have been persisted in postgreSQL.

If manual execution is required:

```bash
python src/quality/persist_dbt_results.py
```

---

## 4. Validation

### Pipeline Status Validation

The Data Engineer shall verify that all DAG tasks are in "success" status.

### Bronze Layer Validation

```sql
SELECT COUNT(*)
FROM bronze.wells_production;
```

### Silver Layer Validation

```sql
SELECT COUNT(*)
FROM silver.silver_wells_production;
```

### Gold Layer Validation

```sql
SELECT COUNT(*)
FROM gold.fact_production;
```

### Data Quality Validation

```sql
SELECT status, COUNT(*)
FROM quality.test_results
GROUP BY status;
```

### Expected Results

The Data Engineer shall confirm:

- Data exists in the bronze layer.
- Data exists in the silver layer.
- Data exists in the gold layer.
- Data quality results have been persisted.
- No critical failures are present in Airflow.

---

## 5. Failure Handling

### Failure in extract_data

#### Possible Causes

- Source system unavailable.
- Network connectivity issues.
- Download timeout.

#### Resolution

The Data Engineer shall:

1. Verify source availability.
2. Review task logs in Airflow.
3. Re-execute the task if necessary.

---

### Failure in load_bronze

#### Possible Causes

- PostgreSQL unavailable.
- Database write failure.
- Storage permission issues.

#### Resolution

The Data Engineer shall:

1. Verify PostgreSQL container status.

```bash
docker ps
```

2. Review airflow logs.
3. Re-execute the task after correcting the issue.

---

### Failure in dbt_run

#### Possible Causes

- Transformation error.
- Compilation error.
- Missing dbt dependencies.

#### Resolution

The Data Engineer shall:

1. Review task logs.
2. Execute:

```bash
dbt deps
dbt run
```

3. Correct the affected model.
4. Re-execute the pipeline.

---

### Failure in dbt_test

#### Possible Causes

- Data quality rule violation.
- Invalid transformed data.
- Referential integrity failure.

#### Resolution

The Data Engineer shall:

1. Identify the failing test.
2. Investigate the affected dataset.
3. Correct the transformation or source data.
4. Re-execute the validation process.

---

### Failure in persist_quality_results

#### Possible Causes

- PostgreSQL unavailable.
- Invalid `run_results.json` file.
- Persistence process failure.

#### Resolution

The Data Engineer shall:

1. Verify database connectivity.
2. Execute the persistence script manually.
3. Confirm that results are stored successfully.

---

### Rollback Procedure

If a deployment introduces failures, the Data Engineer shall revert the corresponding comit and redeploy the previous stable version.

Example:

```bash
git revert <commit_hash>
git push
```

---

## 6. Non-Functional Considerations

### Data Freshness

The platform updates data daily through a scheduled Airflow execution at 06:00 UTC (03:00 am UTC-3, Argentinian time use).

### Data Quality

Data quality controls are implemented using dbt tests.

Results are persisted in:

```text
quality.test_results
```

This enables auditing, monitoring and historical analysis of quality validations.

### Security and Privacy

The platform processes publicly available Oil & Gas production datasets.

No personally identifiable information (PII) is stored or processed.

Credentials and secrets are managed outside the source code.

### Availability

Apache Airflow is configured with automatic retries and backoff exponential to reduce the impact of transient failures.

### Cost Efficiency

The platform runs on a cloud-based infrastructure using a single environment for orchestration, storage and transformation workloads.

### Governance

All code changes must be submitted through pull requests and remain traceable through version control.

---

## Functional Decision Justification

The platform adopts a Medallion architecture composed of bronze, silver and gold layers.

From the Data Engineer perspective, this architecture separates raw ingestion, transformation logic and analytical consumption layers. This separation improves maintainability, simplifies troubleshooting activities and facilitates historical reprocessing.

---

## Non-Functional Decision Justification

The pipeline executes daily at 06:00 UTC (03:00 am UTC-3, Argentinian time use).

From the Data Engineer perspective, daily execution enables early detection of infrastructure failures, integration issues and data quality problems while maintaining up-to-date analytical datasets for downstream consumers.