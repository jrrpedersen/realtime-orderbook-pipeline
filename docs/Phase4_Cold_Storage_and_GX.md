# Phase 4 – Cold Storage & Batch Data Quality Audits

This document describes **Phase 4** of the *Realtime Orderbook Pipeline* project.
Phase 4 introduces a **cold data layer** backed by Parquet files and an **offline
batch data quality audit** using Great Expectations.

The goal of this phase is to demonstrate how validated streaming data can be
persisted for long-term analytics and governed with reproducible quality checks.

---

## 1. Why a Cold Store?

In earlier phases, the pipeline ensured:

- Low-latency ingestion (Kafka)
- Real-time validation
- Reliable hot storage (Postgres)
- Observability (Prometheus & Grafana)

However, production trading systems also require:

- Cost-efficient long-term storage
- Immutable historical datasets
- Batch analytics and backtesting
- Offline data validation and governance

This is the role of the **cold store**.

---

## 2. Cold vs Hot Storage (Conceptual Model)

| Layer | Purpose | Technology |
|-----|--------|-----------|
| Hot store | Low-latency queries, dashboards, real-time usage | Postgres |
| Cold store | Historical analytics, audits, ML, backtesting | Parquet (S3-like) |

Key design principle:

> **Hot and cold paths are written independently from the stream.**
> Data is not copied *from* hot to cold; it is written to both after validation.

---

## 3. Parquet-Based Data Lake

### 3.1 Storage format

Phase 4 uses **Apache Parquet** as the cold storage format.

Benefits:
- Columnar layout
- Highly compressible
- Efficient scans for analytics
- Industry standard for data lakes

---

### 3.2 Partitioning scheme

Parquet files are written using Hive-style partitions:

```
data/lake/
└── symbol=TTF-GAS/
    └── date=YYYY-MM-DD/
        ├── 1234.parquet
        ├── 1235.parquet
        └── ...
```

Partitioning enables:
- Efficient pruning for batch queries
- Symbol- and date-scoped audits
- Straightforward migration to S3-compatible storage

---

### 3.3 Write path

Parquet writing occurs **inside the quality service** after validation:

```
Kafka -> validation -> Postgres (hot)
                    -> Parquet (cold)
```

Only validated ticks are persisted to the cold store.

---

## 4. Parquet Writer Implementation

The writer is implemented in:

```
src/quality_service/parquet_writer.py
```

Key characteristics:
- Append-only, immutable files
- One Parquet file per tick (acceptable for demo scale)
- Automatic directory creation
- Configurable base path via environment variable

Example base path logic:

```python
BASE_PATH = Path(os.getenv("COLD_STORAGE_PATH", DEFAULT_PATH))
```

This mirrors how production pipelines switch between local filesystems and S3.

---

## 5. Offline Batch Data Audits

### 5.1 Motivation

Streaming validation protects real-time systems, but is insufficient alone.

Offline audits are required to:
- Detect silent corruption
- Ensure historical dataset usability
- Support regulatory or analytical guarantees

Phase 4 introduces an explicit **batch audit step**.

---

### 5.2 Audit script

The audit is implemented as a standalone CLI tool:

```
src/data_audit/audit_parquet.py
```

Usage:

```bash
python -m data_audit.audit_parquet   --symbol TTF-GAS   --date 2025-12-09
```

The script:
1. Locates the partition
2. Loads all Parquet files into a DataFrame
3. Applies data quality expectations
4. Emits a validation summary

The audit does **not** require any running services.

---

## 6. Great Expectations Integration

### 6.1 Version pinning

Great Expectations is explicitly pinned to:

```
v0.17.x
```

Rationale:
- Stable, script-friendly API
- No dependency on GX project scaffolding
- Avoids Fluent / DataContext API churn

Version pinning reflects real-world best practices in data platforms.

---

### 6.2 Expectations implemented

The batch audit focuses on **schema and sanity checks**:

- `symbol` must not be null
- `bid_price` must be non-negative
- `ask_price` must be non-negative
- `event_time` must not be null

These checks answer the question:

> “Is this batch safe to use for downstream analytics?”

---

### 6.3 Domain invariants

Cross-column market invariants (e.g. bid < ask) are **enforced earlier** in the
pipeline during streaming validation.

The GX audit deliberately avoids duplicating:
- Real-time business logic
- Domain guarantees already enforced upstream

This separation mirrors production architectures.

---

## 7. Example Output

Successful audit:

```
Loading Parquet data for symbol=TTF-GAS, date=2025-12-09
Loaded 443 rows

Great Expectations summary:
  expect_column_values_to_not_be_null: ✅
  expect_column_values_to_be_between: ✅
  expect_column_values_to_be_between: ✅
  expect_column_values_to_not_be_null: ✅

Overall success: True
```

---

## 8. Design Decisions & Trade-offs

- Immutable cold data simplifies reasoning and governance
- Fine-grained Parquet files prioritize clarity over write efficiency
- Batch connectivity avoided for local reproducibility
- GX expectations scoped to batch-level correctness only

---

## 9. How Phase 4 Fits the Full Pipeline

| Phase | Capability |
|-----|-----------|
| Phase 1 | Streaming ingestion |
| Phase 2 | Validation & hot storage |
| Phase 3 | Monitoring & observability |
| **Phase 4** | **Cold storage & batch audits** |

Together, these phases form a **production-grade data foundation**.

---

## 10. Key Takeaways

- Cold storage is a first-class architectural concern
- Streaming and batch validation serve distinct roles
- Parquet + GX is a powerful combination for data governance
- Version pinning is essential for stable data tooling
- Data quality is enforced across the entire system lifecycle

---

**Phase 4 completes the core data infrastructure required for
trustworthy, auditable, and scalable trading data systems.**
