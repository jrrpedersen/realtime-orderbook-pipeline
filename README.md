# Realtime Orderbook Pipeline

[![Status](https://img.shields.io/badge/Project-Portfolio-green.svg)](#)
[![Phase](https://img.shields.io/badge/Phase-1%20Ingestion-blue.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](#)
[![Kafka](https://img.shields.io/badge/Kafka-Streaming-black.svg)](#)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](#)
[![Async](https://img.shields.io/badge/Async-asyncio-purple.svg)](#)
[![Data](https://img.shields.io/badge/Data-Streaming-orange.svg)](#)
[![Phase](https://img.shields.io/badge/Phase-2%20Kafka%20→%20Postgres-blue.svg)](#)

> **Category:** Data Engineering · Streaming Systems · Trading Infrastructure

This repository is a **toy but production-inspired real-time market data pipeline**, designed to mirror how trading and energy-market data platforms ingest and transport high-frequency data.

Phase 1 focuses on **data ingestion and transport**:

- A Python-based simulator generates realistic orderbook “ticks”
- Kafka acts as the central durable event log
- Ticks are serialized as structured JSON and published to Kafka
- Kafka runs locally via Docker, simulating production infrastructure
- End-to-end data flow is verified using Kafka’s console consumer

Later phases extend the pipeline with validation, storage, monitoring, and APIs.

---

## Architecture (Phases 1–2)

```text
[Price Simulator]
        |
        v
[Kafka topic: orderbook.raw]
        |
        v
[Quality Service]
  - schema validation
  - market integrity checks
        |
        v
[Postgres (hot storage)]
```

---

## Repository Layout

```text
realtime-orderbook-pipeline/
├── README.md
├── .gitignore
├── docker-compose.yml
├── pyproject.toml
├── scripts/
│   └── init_db.sql
└── src/
    ├── common/
    │   ├── __init__.py
    │   ├── models.py
    │   └── config.py
    ├── ingestion_service/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── producer.py
    │   └── simulator.py
    └── quality_service/
        ├── __init__.py
        ├── main.py
        ├── repository.py
        └── validator.py
```

---

## Phase 1 Components

### Domain Model (`common/models.py`)

Defines a typed `OrderBookTick` model using Pydantic:

- `symbol`
- `event_time`
- `received_time`
- `bid_price` / `ask_price`
- `bid_volume` / `ask_volume`
- `sequence_id`

This enforces schema consistency from the moment data is ingested.

---

## Phase 2 – Validation + Hot Storage

Phase 2 extends the pipeline with a **quality service** and **hot storage**.

### What Was Added

- A Kafka consumer (`quality_service`)
- Schema and integrity validation using the domain model
- Asynchronous writes to Postgres
- A durable “hot” database holding validated market data

The pipeline now mirrors a real trading data foundation:

- Kafka as the durable event backbone
- Stateless validation services
- A relational hot store for fast queries and downstream use

---

### Quality Service

The quality service:

- Consumes from the Kafka topic `orderbook.raw`
- Deserializes JSON payloads
- Validates ticks using domain rules:
  - Schema correctness
  - `bid_price < ask_price`
- Writes valid ticks into Postgres

Invalid ticks are dropped (and logged), illustrating how data quality gates are applied in practice.

---

### Hot Storage (Postgres)

Validated ticks are written into a Postgres table:

```sql
ticks (
  symbol,
  event_time,
  received_time,
  bid_price,
  ask_price,
  bid_volume,
  ask_volume,
  sequence_id
);
```

---

## Market Data Simulator (`ingestion_service/simulator.py`)

A simple async random-walk simulator that:

- Generates top-of-book bid/ask prices
- Emits ticks at a configurable frequency
- Maintains a monotonic per-symbol sequence ID
- Mimics the structure of real market data feeds

---

## Kafka Producer (`ingestion_service/producer.py`)

Publishes ticks to Kafka using `aiokafka`:

- Topic: `orderbook.raw`
- Message value: JSON-encoded tick
- Message key: symbol
- Async, non-blocking send loop

---

## Ingestion Entrypoint (`ingestion_service/main.py`)

- Loads configuration from environment variables
- Starts the simulator
- Streams ticks into Kafka
- Logs outgoing events for visibility

This service is structurally similar to a real market data feed handler.

---

## Running Phase 1

### Prerequisites

- Docker / Docker Desktop
- Python 3.11+
- A virtualenv or Conda-based Python environment

---

### 1. Start Kafka

From the project root:

```bash
docker compose up
```

Kafka will be available at:

```text
localhost:9092
```

---

### 2. Install Python Dependencies

```bash
pip install -e .
```

---

### 3. Run the Ingestion Service

```bash
cd src
python -m ingestion_service.main
```

Expected output:

```text
Connecting to Kafka at localhost:9092
Producing ticks for symbol 'TTF-GAS' every 0.05 seconds
Sending tick: {...}
```

---

## Verifying Data in Kafka

```bash
docker ps
docker exec -it <kafka-container-name> bash
```

```bash
kafka-console-consumer   --bootstrap-server localhost:9092   --topic orderbook.raw   --from-beginning
```

---

## Kafka Concept Demonstrated

**Kafka is a log, not a queue**:

- Producers write messages once
- Kafka stores them durably
- Consumers read via offsets
- Messages are not deleted when consumed

---

## Running Phases 1–2 Together

```bash
docker compose up
python -m quality_service.main
cd src
python -m ingestion_service.main
```

Verify Postgres:

```bash
docker exec -it <db-container> psql -U market -d marketdata
```

```sql
SELECT COUNT(*) FROM ticks;
SELECT * FROM ticks ORDER BY event_time DESC LIMIT 10;
```

---

## Roadmap

- ✅ Phase 1 – Ingestion + Kafka
- ✅ Phase 2 – Validation + Postgres (hot storage)
- ⬜ Phase 3 – Monitoring (Prometheus + Grafana)
- ⬜ Phase 4 – Cold storage (Parquet / S3-style) + Great Expectations
- ⬜ Phase 5 – API layer, replay, and resilience patterns

---

## Motivation

Inspired by real-world trading and market-data systems handling:

- High-frequency feeds
- Data quality guarantees
- Hot / cold storage patterns
- Operational observability

---

## Technology Stack / Tags

Python · Kafka · Streaming Data · Market Data · Orderbook · Data Engineering · Event-Driven Architecture · Async IO · Docker · Trading Systems