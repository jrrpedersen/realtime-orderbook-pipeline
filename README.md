# Realtime Orderbook Pipeline (Phase 1 – Ingestion + Kafka)

This repository is a **toy but production-inspired real-time market data pipeline**, designed to mirror how trading and energy-market data platforms ingest and transport high-frequency data.

Phase 1 focuses on **data ingestion and transport**:

- A Python-based simulator generates realistic orderbook “ticks”
- Kafka acts as the central durable event log
- Ticks are serialized as structured JSON and published to Kafka
- Kafka runs locally via Docker, simulating production infrastructure
- End-to-end data flow is verified using Kafka’s console consumer

Later phases will extend the pipeline with validation, storage, monitoring, and APIs.

---

## Architecture (Phase 1)

```text
[Price Simulator] --(JSON ticks)--> [Kafka topic: orderbook.raw]
```

---

## Repository layout

```
realtime-orderbook-pipeline/
├── README.md
├── .gitignore
├── docker-compose.yml
├── pyproject.toml
└── src/
    ├── common/
    │   ├── __init__.py
    │   └── models.py
    └── ingestion_service/
        ├── __init__.py
        ├── main.py
        ├── producer.py
        └── simulator.py
```

---

## Phase 1 components

### Domain model (`common/models.py`)
Defines a typed `OrderBookTick` model using Pydantic:

- `symbol`
- `event_time`
- `received_time`
- `bid_price` / `ask_price`
- `bid_volume` / `ask_volume`
- `sequence_id`

This enforces schema consistency from the moment data is ingested.

---

### Market data simulator (`ingestion_service/simulator.py`)
A simple async random-walk simulator that:

- Generates top-of-book bid/ask prices
- Emits ticks at a configurable frequency
- Maintains a monotonic per-symbol sequence ID
- Mimics the shape of real market data feeds

---

### Kafka producer (`ingestion_service/producer.py`)
Publishes ticks to Kafka using `aiokafka`:

- Topic: `orderbook.raw`
- Message value: JSON-encoded tick
- Message key: symbol
- Async, non-blocking send loop

---

### Ingestion entrypoint (`ingestion_service/main.py`)
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
- A virtual or Conda-based Python environment

---

### 1. Start Kafka

From the project root:

```bash
docker compose up
```

Kafka will be available at:

```
localhost:9092
```

---

### 2. Install Python dependencies

In the same environment you will run Python from:

```bash
pip install -e .
```

This installs the project in editable mode along with its dependencies.

---

### 3. Run the ingestion service

From the `src` directory:

```bash
cd src
python -m ingestion_service.main
```

You should see output similar to:

```
Connecting to Kafka at localhost:9092
Producing ticks for symbol 'TTF-GAS' every 0.05 seconds
Sending tick: {...}
```

At this point, ticks are being generated and published continuously to Kafka.

---

## Verifying data in Kafka

Kafka stores messages independently of consumers. To verify ingestion:

1. List running containers:

```bash
docker ps
```

2. Open a shell in the Kafka container:

```bash
docker exec -it <kafka-container-name> bash
```

3. Consume messages from the topic:

```bash
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic orderbook.raw \
  --from-beginning
```

You should see JSON-encoded ticks printed to the terminal.

This confirms that:

- Kafka has accepted and persisted the data
- Messages can be consumed independently of the producer
- The ingestion pipeline is working end-to-end

---

## Kafka concept demonstrated

**Kafka is a log, not a queue**:

- Producers write messages once
- Kafka stores them durably for a retention period
- Consumers read data using offsets
- Messages are not deleted when consumed

This enables replay, multiple independent consumers, and safe downstream processing.

---

## Roadmap

Planned next phases:

1. ✅ Phase 1 – Ingestion + Kafka
2. Phase 2 – Validation service + Postgres (hot storage)
3. Phase 3 – Monitoring with Prometheus + Grafana
4. Phase 4 – Cold storage (Parquet / S3-style) + Great Expectations
5. Phase 5 – API layer, replay, and resilience patterns

---

## Motivation

This project is inspired by real-world trading and data-engineering systems, particularly those handling:

- high-frequency market data
- orderbook feeds
- data quality guarantees
- hot / cold storage patterns
- operational observability