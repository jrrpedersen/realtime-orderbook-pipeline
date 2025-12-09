# Realtime Orderbook Pipeline

[![Phase](https://img.shields.io/badge/Phase-3%20Monitoring-blue.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](#)
[![Kafka](https://img.shields.io/badge/Kafka-Streaming-black.svg)](#)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](#)
[![Async](https://img.shields.io/badge/Async-asyncio-purple.svg)](#)
[![Data](https://img.shields.io/badge/Data-Streaming-orange.svg)](#)
[![Observability](https://img.shields.io/badge/Observability-Prometheus%20%2B%20Grafana-orange.svg)](#)
[![Parquet](https://img.shields.io/badge/Parquet-Cold_Store-orange.svg)](#)

> **Category:** Data Engineering · Streaming Systems · Trading Infrastructure

A **production-inspired real-time data pipeline** for ingesting, validating, storing, monitoring, and auditing high-frequency orderbook data.

This project demonstrates how to build a **trustworthy data foundation** for trading and analytics systems, with explicit attention to data quality, fault tolerance, observability, and hot vs. cold storage separation.

---

## 🧩 Problem Statement

Modern trading systems rely on data that is:
- always available
- timely
- internally consistent
- auditable after the fact

This project models a realistic data foundation for such systems:
- real-time ingestion of orderbook events
- streaming validation safeguards
- low-latency “hot” storage
- immutable “cold” historical storage
- batch-level data quality audits
- full system observability

---

## 🏗 High-Level Architecture

```
            +-------------------+
            |  Ingestion Service |
            |  (Python, Kafka)  |
            +---------+---------+
                      |
                      v
                Kafka (raw ticks)
                      |
                      v
            +-------------------+
            |  Quality Service  |
            |  - schema checks |
            |  - domain rules  |
            +----+---------+---+
                 |         |
                 |         |
                 v         v
         Postgres (Hot)   Parquet Lake (Cold)
             |                 |
             |                 v
             |         Batch Quality Audits
             |       (Great Expectations)
             |
     Dashboards / Queries

Monitoring:
Ingestion + Quality services → Prometheus → Grafana
```

---

## 📦 Project Structure

```
realtime-orderbook-pipeline/
├── src/
│   ├── ingestion_service/
│   ├── quality_service/
│   ├── data_audit/
│   └── common/
├── data/
│   └── lake/
├── infra/
│   ├── prometheus/
│   └── grafana/
├── docs/
│   ├── Phase3_Observability.md
│   └── Phase4_Cold_Storage_and_GX.md
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## 🔁 Pipeline Phases

### Phase 1 – Ingestion & Streaming
- Simulated high-frequency orderbook ticks
- Kafka as a durable, decoupled buffer

### Phase 2 – Streaming Validation & Hot Storage
- Schema and domain validation
- Valid data persisted to Postgres

### Phase 3 – Observability
- Prometheus metrics exposed by services
- Grafana dashboards for system health

### Phase 4 – Cold Storage & Batch Audits
- Parquet-based data lake
- Offline Great Expectations audits

---

## 🔥 Hot vs ❄️ Cold Storage

| Layer | Purpose | Technology |
|-----|-------|------------|
| Hot store | Low-latency queries | Postgres |
| Cold store | Historical analytics | Parquet |

Data is written to hot and cold stores independently after validation.

---

## ✅ Data Quality Strategy

**Streaming (real-time):**
- Enforced in the quality service

**Batch (offline):**
- Great Expectations over Parquet data

---

## 📊 Observability

Each service exposes Prometheus metrics.
Grafana provides real-time dashboards for ingestion and validation throughput.

---

## 🧪 Running the Project Locally

```bash
docker-compose up -d
```

```bash
cd src
python -m ingestion_service.main
```

```bash
cd src
python -m quality_service.main
```

```bash
python -m data_audit.audit_parquet --symbol TTF-GAS --date 2025-12-09
```

---

## 🧠 Design Decisions

- Kafka for reliable streaming
- Parquet for long-term storage
- Explicit separation of streaming and batch validation
- Version-pinned data tooling

---

## 🚀 Future Extensions

- Parquet compaction
- Retention policies
- Schema evolution
- Flink-based processing


---

## Technology Stack / Tags

Python · Kafka · Streaming Data · Market Data · Orderbook · Data Engineering · Event-Driven Architecture · Async IO · Docker · Trading Systems · Prometheus · Grafana