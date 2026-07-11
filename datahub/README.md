# DataHub — Data Catalog & Governance

Runs [DataHub](https://datahubproject.io/) locally as a metadata catalog over the
project's Medallion Architecture: searchable datasets, ownership, documentation and
lineage across the `bronze`/`silver`/`gold` PostgreSQL schemas and the dbt project.

## Status

DataHub is **not** part of the shared deployment described in the main
[README](../README.md) — it does not run on the EC2 instance and there is no public
URL for it. It runs on demand, on whichever machine needs to browse the catalog, via
the Docker Compose file in this folder. Treat the steps below as the source of truth
for whether DataHub is actually running — don't assume it is just because this folder
exists.

## 1. Start the DataHub backend

```bash
docker compose -f datahub/docker-compose.yml up -d
```

This brings up Kafka, MySQL, OpenSearch, and the DataHub GMS + frontend (6 containers).
The first start downloads several GB of images and can take a few minutes; later
starts are fast. Wait until `datahub-gms` reports healthy:

```bash
docker compose -f datahub/docker-compose.yml ps
```

Once healthy:
- **Catalog UI (open this in a browser): http://localhost:9002** — login `datahub` / `datahub`.
- GMS (ingestion API, used by the recipes below, not meant to be browsed): http://localhost:8080.
  Opening `http://localhost:8080/` directly in a browser is expected to show a
  "Whitelabel error page" / 500 on `/` — GMS has no home page, it only serves the
  REST/GraphQL API and `/health`. That is not a sign anything is broken; check
  `docker compose -f datahub/docker-compose.yml ps` or `curl http://localhost:8080/health`
  instead.

> `datahub-gms` publishes host port 8080 by default — the same port the main
> `../docker-compose.yml` uses for `webhook-receiver`. If you need both stacks running
> at once on the same machine, set `DATAHUB_GMS_PORT` (e.g. `8081`) before starting
> this compose file, and point `recipe_postgres.yml` / `recipe_dbt.yml` at that port.

## 2. Ingest metadata

Install the CLI, pinned to match the server version used in `docker-compose.yml`:

```bash
pip install -r datahub/requirements.txt
```

`recipe_postgres.yml` scans the `bronze`/`silver`/`gold` schemas directly from
PostgreSQL. `recipe_dbt.yml` enriches the catalog with dbt model/column descriptions,
test results and lineage, read from `oil_gas_dbt/target/manifest.json` and
`catalog.json` — generate those first:

```bash
cd oil_gas_dbt && dbt docs generate && cd ..
./datahub/ingest.sh
```

This is a manual step on purpose — it is **not** wired into the `oil_gas_pipeline` Airflow
DAG. Airflow runs on the shared EC2 instance, where there is no DataHub server to ingest
into; an automated task there would simply fail every day. See "Airflow Integration" in
[adrs/14. ADR_DataGovernance.md](../adrs/14.%20ADR_DataGovernance.md) for the reasoning.
The catalog reflects whatever was last ingested here, not necessarily the latest pipeline
run.

## 3. Stop

```bash
docker compose -f datahub/docker-compose.yml down      # keep the catalog data
docker compose -f datahub/docker-compose.yml down -v   # also wipe it
```

## Files

| File | Purpose |
|---|---|
| `docker-compose.yml` | Standalone DataHub backend (Kafka, MySQL, OpenSearch, GMS, frontend). |
| `recipe_postgres.yml` | Ingests table/column metadata from the `oilgas` Postgres database. |
| `recipe_dbt.yml` | Ingests dbt model docs, tests and lineage. |
| `ingest.sh` | Runs both recipes in order. |
| `requirements.txt` | Pinned `acryl-datahub` CLI version. |
