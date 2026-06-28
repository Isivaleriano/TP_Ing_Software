#!/bin/bash
# Runs the metadata ingestion recipes against the DataHub stack started with
# `docker compose -f datahub/docker-compose.yml up -d`.
#
# Requires the DataHub CLI (see requirements.txt) and a running, healthy
# datahub-gms container reachable at the host:port configured in the recipes
# (http://localhost:8080 by default).
set -euo pipefail
cd "$(dirname "$0")"

datahub ingest -c recipe_postgres.yml
datahub ingest -c recipe_dbt.yml
