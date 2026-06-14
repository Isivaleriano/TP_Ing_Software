---
status: Accepted
date: 13/06/2026
decision-makers: Isidro Valeriano
consulted: Florencia Zoffi, María Belén Depalo
informed: none
---

# Data Quality Persistence Strategy

## Context and Problem Statement

Data quality checks are defined in dbt schema.yml files covering uniqueness,
not-null, referential integrity, accepted values and range validations. However
by default dbt test results only exist in memory and in a local JSON file,
not in the data warehouse. A mechanism was needed to persist these results
and enforce operational consequences when checks fail.

## Decision Drivers

* Quality results must be persisted beyond runtime and not just asserts
* Failed quality checks must have an operational consequence
* Results must be queryable and auditable over time
* The solution must integrate with the existing airflow pipeline

## Considered Options

* Persist dbt test results to postgreSQL via a custom python script
* Use dbt's built-in store_failures configuration
* Do not persist results (runtime only)

## Decision Outcome

Chosen option: "Persist dbt test results to postgreSQL via a custom python script",
because it gives full control over the schema and allows querying results from
Metabase. The script reads dbt's run_results.json after each test run and inserts
the results into a quality.test_results table in postgreSQL.

### Consequences

* Good, because quality results are persisted and queryable from Metabase
* Good, because the quality schema is isolated from silver and gold data
* Good, because failed error-severity tests block downstream promotion via Airflow
* Good, because results accumulate over time providing an audit trail
* Bad, because it requires maintaining a custom script in addition to dbt configuration
* Bad, because it depends on dbt writing run_results.json before the script runs

### Confirmation

The persist_quality_results task runs after dbt_test in the Airflow DAG. Results
are stored in the quality.test_results table in postgreSQL and are visible in
Metabase under the quality schema.

## Pros and Cons of the Options

### Persist dbt test results to PostgreSQL via a custom Python script

* Good, because results are immediately queryable from Metabase
* Good, because the schema is fully customizable
* Neutral, because it adds one more task to the Airflow DAG
* Bad, because it requires maintaining additional code

### Use dbt's built-in store_failures configuration

* Good, because it is native to dbt and requires no additional code
* Good, because it stores failing rows directly in the data warehouse
* Bad, because it only stores failing rows, not a summary of all test executions
* Bad, because it does not integrate as cleanly with the Airflow pipeline

### Do not persist results (runtime only)

* Good, because no additional implementation is required
* Bad, because quality results are lost after each pipeline run
* Bad, because there is no audit trail of quality over time

## More Information

The quality.test_results table is created automatically by the
persist_dbt_results.py script if it does not exist. The table stores one row
per dbt test per pipeline run, including invocation_id, test name, status,
failures count and execution time.