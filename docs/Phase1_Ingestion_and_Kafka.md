# Phase 1 – Real-Time Orderbook Pipeline (Ingestion + Kafka)

## Project description (for GitHub)

This project is a **toy but production-inspired real-time market data pipeline**, designed to demonstrate how high‑frequency trading and analytics systems ingest, transport, and validate streaming data.

Phase 1 focuses on **data ingestion and transport**:

- A Python-based market data simulator generates realistic orderbook ticks
- Kafka is used as the central durable event log
- Ticks are serialized as structured JSON and published to Kafka topics
- Kafka is run locally using Docker, simulating real infrastructure
- Data flow is verified using Kafka’s console consumer

The project is intentionally structured like a real production system (with `src/` layout, typed models, async IO, and containerized infrastructure) so it can be extended in later phases with validation, hot/cold storage, monitoring, and APIs.

---

## Goals of Phase 1

✅ Establish a clean project and repository structure  
✅ Model market data using typed schemas  
✅ Simulate a real-time market data feed  
✅ Publish streaming data to Kafka  
✅ Run Kafka locally via Docker  
✅ Verify that data is stored and consumable  

This phase answers the core question:

> “Can we reliably get structured, real‑time data into Kafka?”

---

## Repository structure (Phase 1)

```
realtime-orderbook-pipeline/
├── README.md
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

### Key components

### `common/models.py`
Defines a Pydantic model for structured market data:

- symbol
- bid / ask price
- bid / ask volume
- timestamps
- per-symbol sequence ID

This enforces schema consistency from the first step of ingestion.

---

### `ingestion_service/simulator.py`
A simple **random-walk market simulator**:

- Generates ticks for a symbol (e.g. `TTF-GAS`)
- Controls tick frequency via a configurable interval
- Maintains a monotonic sequence ID
- Mimics top-of-book bid/ask behaviour

---

### `ingestion_service/producer.py`
Kafka producer logic using `aiokafka`:

- Serializes ticks as JSON
- Uses symbol as the Kafka message key
- Publishes messages to the topic `orderbook.raw`
- Prints ticks for visibility during development

---

### `ingestion_service/main.py`
The entrypoint:

- Reads configuration from environment variables
- Starts the simulator
- Streams ticks asynchronously into Kafka
- Intended to be structurally similar to a real ingestion/feed‑handler service

---

## Kafka setup (Docker)

Kafka (and Zookeeper) are run using Docker Compose.

### `docker-compose.yml` (Phase 1)

Kafka is configured to:

- Run entirely locally
- Be reachable from the host at `localhost:9092`
- Persist messages independently of consumers

Key concept:

> Kafka stores messages whether or not anyone is consuming them.

---

## Running Phase 1 locally

### 1. Start Kafka

From the project root:

```bash
docker compose up
```

Kafka will be available on:

```
localhost:9092
```

---

### 2. Install Python dependencies

In the same environment you will run Python from:

```bash
pip install -e .
```

---

### 3. Start the ingestion service

From the `src/` directory:

```bash
python -m ingestion_service.main
```

You should see output like:

```
Connecting to Kafka at localhost:9092
Producing ticks for symbol 'TTF-GAS' every 0.05 seconds
Sending tick: {...}
Sending tick: {...}
```

At this point:

✅ ticks are being generated  
✅ ticks are being published to Kafka  

---

## Verifying data inside Kafka

To confirm that Kafka is actually storing messages (independent of producers):

### 1. Open a shell inside the Kafka container

```bash
docker ps
docker exec -it <kafka-container-name> bash
```

---

### 2. List or create the topic

```bash
kafka-topics --bootstrap-server localhost:9092 --list
```

If needed:

```bash
kafka-topics   --bootstrap-server localhost:9092   --create   --topic orderbook.raw   --partitions 1   --replication-factor 1
```

---

### 3. Consume messages

```bash
kafka-console-consumer   --bootstrap-server localhost:9092   --topic orderbook.raw   --from-beginning
```

You should see the JSON‑encoded ticks printed to the terminal.

This proves:

✅ Kafka has received the data  
✅ Messages are persisted  
✅ Consumers can read the data independently  

---

## Key Kafka concept demonstrated

> **Kafka is a log, not a queue.**

- Producers write messages once
- Kafka stores them durably
- Consumers read independently using offsets
- Messages are NOT deleted when consumed

This design allows:

- replaying historical data
- multiple consumers reading the same stream
- safe downstream processing in later pipeline stages

---

## Outcome of Phase 1

By the end of Phase 1, we have:

✅ A real-time data source  
✅ A durable event backbone (Kafka)  
✅ A production‑style project structure  
✅ Verified end‑to‑end data flow  

This provides the foundation for:

- Phase 2: Kafka consumer + validation + Postgres  
- Phase 3: Monitoring (Prometheus/Grafana)  
- Phase 4: Cold storage (Parquet / S3) + Great Expectations  
- Phase 5: APIs, dashboards, and resilience patterns  

---

## Next steps

The logical next phase is to build a **quality service** that:

- consumes from Kafka
- validates schema and market invariants
- writes clean data to a hot store (Postgres)

This mirrors exactly how real trading data platforms are built.
