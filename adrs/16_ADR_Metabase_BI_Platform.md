---
status: Accepted
date: 13/06/2026
decision-makers: Isidro Valeriano
consulted: Florencia Zoffi, María Belén Depalo
informed: none
---

# BI Platform for Oil & Gas Data Exploration

## Context and Problem Statement

The system requires a BI platform where non-technical users such as planning
analysts and reservoir engineers can explore and visualize production data
without writing SQL. The platform needs to connect to the PostgreSQL data
warehouse and expose the Gold layer tables built by dbt.

## Decision Drivers

* Non-technical users must be able to explore data without writing SQL
* The platform must connect to the existing PostgreSQL data warehouse
* The solution must be deployable as a Docker container alongside existing services

## Considered Options

* Metabase
* Apache Superset
* Grafana

## Decision Outcome

Chosen option: "Metabase", because it has the simplest setup process, requires
no configuration files to connect to postgreSQL, and automatically discovers
tables and schemas. It provides an intuitive UI suitable for non-technical users
out of the box.

### Consequences

* Good, because it connects to postgreSQL with minimal configuration
* Good, because it automatically discovered bronze, silver, gold and public schemas
* Good, because non-technical users can explore data without SQL knowledge
* Good, because it deploys as a single docker container
* Bad, because it uses postgreSQL as its own metadata database, sharing the
  same instance used for the data warehouse
* Bad, because the free open-source version has limited enterprise features

### Confirmation

Metabase is deployed and accessible on port 3000. It is connected to the oilgas
postgreSQL database and exposes all schemas including the gold layer tables
built by dbt.

## Pros and Cons of the Options

### Metabase

* Good, because setup is minimal, no configuration files required
* Good, because it automatically discovers tables and schemas
* Good, because the UI is intuitive for non-technical users
* Neutral, because it uses PostgreSQL as its metadata store
* Bad, because advanced features require the paid enterprise version

### Apache Superset

* Good, because it is highly customizable and feature-rich
* Good, because it supports complex visualizations
* Bad, because setup requires more configuration and time
* Bad, because the learning curve is steeper for non-technical users

### Grafana

* Good, because we already had it deployed for monitoring
* Bad, because it is designed for time-series metrics, not analytical exploration
* Bad, because it is not suitable for non-technical business users

## More Information

Metabase is defined in docker-compose.yml and connects to oilgas_postgres on
port 5432. The UI is accessible at port 3000 of the EC2 instance.