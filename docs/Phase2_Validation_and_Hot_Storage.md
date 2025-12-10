# Phase 2 – Validation Service & Hot Storage (Kafka → Postgres)

This document provides **detailed internal documentation for Phase 2** of the
Realtime Orderbook Pipeline project. It is intended as a personal reference and
design rationale document, explaining *why* components exist and *how* data
flows through the system.

Phase 2 builds directly on Phase 1 and introduces **data validation** and a
**hot storage layer**, closely mirroring real-world trading and data engineering
architectures.

---

## 1. Objectives of Phase 2

Phase 2 answers the question:

> “How do we move from raw streaming data to trusted, queryable data that the
> business can use?”

The concrete goals were:

- Consume raw streaming data from Kafka
- Enforce data quality and domain invariants
- Persist only valid data
- Store validated data in a low-latency hot database
- Keep services stateless and horizontally scalable

---

## 2. High-level architecture

```text
┌─────────────────────┐
│  Ingestion Service  │
│  (simulated feed)   │
└─────────┬───────────┘
          │ JSON ticks
          ▼
┌─────────────────────┐
│        Kafka        │
│ topic: orderbook.raw│
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   Quality Service   │
│  - schema checks    │
│  - integrity rules  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│     Postgres DB     │
│   (hot storage)     │
└─────────────────────┘
```

Key architectural principles:

- Kafka is the **system of record** for all raw events
- Validation is done in isolated, stateless services
- Hot storage only contains *validated* data
- Services communicate only through Kafka and the database

---

## 3. Role of Kafka in Phase 2

Kafka remains the central backbone.

### Important properties leveraged:

- **Durability** – messages are stored independent of consumers
- **Replayability** – consumers can reprocess data from earlier offsets
- **Fan-out** – multiple consumers can read the same topic independently
- **Consumer groups** – horizontal scaling via group membership

In Phase 2:

- Topic: `orderbook.raw`
- Producer: `ingestion_service`
- Consumer group: `quality-service`

Kafka offsets track how much data the quality service has processed.

---

## 4. Quality service design

The quality service is implemented in `src/quality_service/`.

### Responsibilities

- Deserialize JSON messages from Kafka
- Validate schema using the domain model
- Apply basic market integrity rules
- Persist valid ticks into Postgres
- Drop (and log) invalid ticks

### Why a separate service?

In real trading/data platforms:

- Validation logic changes frequently
- Multiple validation strategies may coexist
- Services must be restartable without data loss

Separating validation into its own service ensures:

- Loose coupling
- Easy replay from Kafka
- Independent scaling

---

## 5. Validation logic

Validation is intentionally split into two layers:

### 5.1 Schema validation

Using the shared domain model (`OrderBookTick`):

```python
tick = OrderBookTick(**raw_dict)
```

This enforces:

- Required fields present
- Correct data types
- Basic value constraints (e.g. volumes ≥ 0)

Schema errors are handled gracefully and do not crash the service.

---

### 5.2 Domain integrity checks

Example rule implemented in Phase 2:

```text
bid_price < ask_price
```

This reflects a fundamental property of an orderbook.

Invalid ticks are rejected before reaching storage, protecting downstream users.

---

## 6. Hot storage: why Postgres?

Postgres is used as the **hot data store**.

### Rationale

In real systems, hot storage is optimized for:

- Fast ad-hoc queries
- Dashboards
- APIs
- Recent historical analysis

Postgres offers:

- Strong consistency
- Indexing and SQL
- Operational familiarity
- Excellent ecosystem support

Cold data (long-term, high-volume storage) will be introduced later.

---

## 7. Database schema

The `ticks` table is created automatically via `scripts/init_db.sql`.

```sql
CREATE TABLE ticks (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    received_time TIMESTAMPTZ NOT NULL,
    bid_price DOUBLE PRECISION NOT NULL,
    ask_price DOUBLE PRECISION NOT NULL,
    bid_volume DOUBLE PRECISION NOT NULL,
    ask_volume DOUBLE PRECISION NOT NULL,
    sequence_id BIGINT NOT NULL
);
```

### Design notes

- No foreign keys (append-only fact table)
- Optimized for write throughput and time-based queries
- Indexed by `(symbol, event_time DESC)`

---

## 8. Service scalability and fault tolerance

### Kafka consumer behavior

- Consumer group ensures only one instance processes a partition
- Restarting the service resumes from last committed offset
- Crashes do not lose data (Kafka retains messages)

### Postgres interaction

- Async connection pool via `asyncpg`
- Stateless inserts
- Can be throttled or guarded with backpressure if needed later

---

## 9. Observed startup warnings (and why they are OK)

During development, the following warnings may appear:

```text
Topic orderbook.raw is not available during auto-create initialization
GroupCoordinatorNotAvailableError
```

These occur when:

- Kafka is still initializing
- Topics are auto-created
- Consumer group coordination is not yet ready

The client retries automatically and continues once Kafka stabilizes.

In production, topics would typically be pre-created, eliminating this noise.

---

## 10. Verification performed

Phase 2 was validated by:

- Running ingestion and quality services simultaneously
- Observing steady inserts into Postgres
- Querying the database directly:

```sql
SELECT COUNT(*) FROM ticks;
SELECT * FROM ticks
ORDER BY event_time DESC
LIMIT 10;
```

Successful results confirm:

- End-to-end data flow
- Correct consumer behavior
- Correct Postgres persistence

---

## 11. How Phase 2 fits the long-term design

Phase 2 establishes:

- Kafka as the durable source of truth
- A clean boundary between raw and trusted data
- A realistic hot storage layer

This sets up future phases cleanly:

- Phase 3 – Observability (Prometheus + Grafana)
- Phase 4 – Cold storage (Parquet / S3-style) + Great Expectations
- Phase 5 – APIs, replay, and resilience patterns

---

## 12. Key takeaways

- Kafka ingestion alone is not sufficient for reliable analytics
- Validation as a first-class component is essential
- Hot storage should only contain trusted data
- Event-driven architectures enable replay and resilience

Phase 2 moves the project from “data streaming demo” to
**a realistic data foundation architecture**.
