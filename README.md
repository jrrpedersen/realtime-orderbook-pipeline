# Realtime Orderbook Pipeline

[![Phase](https://img.shields.io/badge/Phase-3%20Monitoring-blue.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](#)
[![Kafka](https://img.shields.io/badge/Kafka-Streaming-black.svg)](#)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](#)
[![Async](https://img.shields.io/badge/Async-asyncio-purple.svg)](#)
[![Data](https://img.shields.io/badge/Data-Streaming-orange.svg)](#)
[![Phase](https://img.shields.io/badge/Phase-2%20Kafka%20→%20Postgres-blue.svg)](#)
[![Observability](https://img.shields.io/badge/Observability-Prometheus%20%2B%20Grafana-orange.svg)](#)

> **Category:** Data Engineering · Streaming Systems · Trading Infrastructure

This repository demonstrates a **production-inspired real-time data pipeline** for market and trading data.
It simulates high-frequency orderbook ticks, processes them through a streaming backbone, enforces data quality,
persists trusted data, and exposes operational metrics for observability.

The project is built incrementally in phases to mirror how real trading data platforms evolve.

---

## Architecture (Phases 1–3)

```text
[Price Simulator]
        |
        v
[Kafka topic: orderbook.raw]
        |
        v
[Quality Service]
  - schema validation
  - domain checks
        |
        v
[Postgres (hot storage)]

Monitoring:
[Ingestion Service] ---> /metrics ---> Prometheus ---> Grafana
[Quality Service]   ---> /metrics ---> Prometheus ---> Grafana
```

---

## Phase 1 – Ingestion & Kafka

**Goal:** Reliable, replayable ingestion of streaming market data.

### What is implemented

- Python-based ingestion service
- Simulated orderbook tick generator
- Kafka as a durable, replayable event log
- JSON serialization for events
- Docker Compose–based local infrastructure

Kafka acts as the system of record for all raw market events.

---

## Phase 2 – Validation & Hot Storage

**Goal:** Convert raw events into trusted, queryable data.

### What is implemented

- Kafka consumer service (quality service)
- Schema validation using a shared domain model
- Basic market integrity checks (e.g. bid < ask)
- Asynchronous writes to Postgres
- Append-only hot storage for validated ticks

Only validated data is persisted, protecting downstream consumers.

---

## Phase 3 – Observability & Monitoring

**Goal:** Make the pipeline observable and production-ready.

### What is implemented

- Prometheus for metrics collection
- Grafana for visualization
- Application-level metrics emitted by services:
  - ticks produced
  - ticks validated / rejected
  - database inserts
  - ingestion lag
- Live dashboards showing pipeline health and throughput

Prometheus scrapes metrics from each service via `/metrics`.
Grafana queries Prometheus to visualize trends and rates.

---

## Project Structure

```text
realtime-orderbook-pipeline/
├── README.md
├── .gitignore
├── docker-compose.yml
├── pyproject.toml
├── scripts/
│   └── init_db.sql
├── infra/
│   └── prometheus/
│       └── prometheus.yml
└── src/
    ├── common/
    │   ├── models.py
    │   ├── config.py
    │   └── metrics.py
    ├── ingestion_service/
    │   ├── main.py
    │   ├── producer.py
    │   └── simulator.py
    └── quality_service/
        ├── main.py
        ├── repository.py
        └── validator.py
```

---

## Running the Pipeline Locally

### 1. Start infrastructure services

```bash
docker compose up
```

This starts:
- Kafka + Zookeeper
- Postgres (hot storage)
- Prometheus
- Grafana

---

### 2. Start the quality service

```bash
cd src
python -m quality_service.main
```

Consumes from Kafka, validates ticks, writes to Postgres, and exposes metrics.

---

### 3. Start the ingestion service

```bash
cd src
python -m ingestion_service.main
```

Produces simulated orderbook ticks to Kafka and exposes metrics.

---

## Verifying the Pipeline

### Kafka

Validate consumption using Kafka console tools or by observing the quality service logs.

---

### Postgres

Connect to Postgres and inspect stored ticks:

```sql
SELECT COUNT(*) FROM ticks;
SELECT symbol, event_time, bid_price, ask_price
FROM ticks
ORDER BY event_time DESC
LIMIT 10;
```

---

### Prometheus

Open:
```
http://localhost:9090
```

Example queries:
```promql
rate(ticks_produced_total[1m])
rate(ticks_valid_total[1m])
```

---

### Grafana

Open:
```
http://localhost:3000
```

(Default credentials: `admin` / `admin`)

Create dashboards using Prometheus queries to visualize:
- ingestion throughput
- validation rates
- lag distributions

---

## Design Notes

- Kafka provides durability, replay, and decoupling
- Validation is isolated in a stateless service
- Postgres serves as a hot, queryable store
- Observability is treated as a first-class concern
- The system favors simplicity and clarity over premature complexity

Technologies like Flink or Elasticsearch are natural future extensions but are intentionally not introduced yet.

---

## Roadmap

✅ Phase 1 – Ingestion + Kafka  
✅ Phase 2 – Validation + Postgres (hot storage)  
✅ Phase 3 – Monitoring with Prometheus & Grafana  
⬜ Phase 4 – Cold storage (Parquet / S3-style) + data quality frameworks  
⬜ Phase 5 – APIs, replay workflows, and resilience patterns

---

## Disclaimer

This project is for learning and demonstration purposes.
It intentionally simplifies aspects such as authentication, security, and scaling,
while preserving core architectural and operational concepts used in production systems.

---

## Technology Stack / Tags

Python · Kafka · Streaming Data · Market Data · Orderbook · Data Engineering · Event-Driven Architecture · Async IO · Docker · Trading Systems · Prometheus · Grafana