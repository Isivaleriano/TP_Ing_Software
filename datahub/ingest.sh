#!/bin/bash

datahub ingest -c recipe_postgres.yml
datahub ingest -c recipe_dbt.yml