# Phase 3 – Observability with Prometheus & Grafana

This document provides **detailed internal documentation for Phase 3** of the
Realtime Orderbook Pipeline project. It explains the motivation for monitoring,
the role of each component, and how the Phase 3 code integrates with existing
ingestion and validation services.

Phase 3 focuses on **making the system observable**: understanding throughput,
health, and latency of a real-time streaming pipeline.

---

## 1. Objectives of Phase 3

Phase 3 answers the question:

> “How do we know that the data pipeline is healthy, performant, and trustworthy
> while it is running?”

The concrete goals were:

- Expose meaningful application-level metrics
- Track ingestion and validation throughput
- Detect failures and anomalies early
- Visualize system behavior in real time
- Lay the groundwork for alerting

Observability is treated as a **first-class concern**, not an afterthought.

---

## 2. High-level monitoring architecture

```text
[Ingestion Service] ---> /metrics ---> Prometheus                                                ---> Grafana Dashboards
[Quality Service]   ---> /metrics ---> Prometheus /
```

Key ideas:

- Services **emit metrics**, but do not store them
- Prometheus **scrapes** metrics periodically
- Grafana **queries Prometheus**
- No service depends on Grafana or Prometheus for correctness

---

## 3. Role of Prometheus

Prometheus is responsible for:

- Periodically scraping `/metrics` endpoints
- Storing time-series metric data
- Evaluating PromQL queries
- Serving as the backend for dashboards and alerts

Prometheus does **not**:
- Drive business logic
- Control services
- Replace logging

It is a **passive observer**.

---

## 4. Role of Grafana

Grafana is the visualization layer.

Grafana:
- Connects to Prometheus as a data source
- Executes PromQL queries
- Displays time-series dashboards
- Allows interactive exploration of metrics

Grafana does **not** collect metrics itself and does not replace Prometheus.

---

## 5. Metrics definition (code-level)

All Phase 3 metrics are defined in:

```text
src/common/metrics.py
```

This centralization ensures consistency and avoids metric duplication.

### Metrics defined

- `ticks_produced_total`
- `ticks_valid_total`
- `ticks_invalid_total`
- `db_inserts_total`
- `ingestion_lag_seconds`

Each metric uses **labels** such as:
- `service`
- `symbol`
- `reason` (for failures)

Labels allow metrics to be sliced and aggregated dynamically in PromQL.

---

## 6. Instrumentation: ingestion service

### Files involved

```text
src/ingestion_service/
├── main.py
└── producer.py
```

### Key responsibilities

- Increment `ticks_produced_total`
- Expose `/metrics` on a dedicated HTTP port

### How it works

1. Metrics are imported from `common.metrics`
2. The producer increments counters as ticks are produced
3. `prometheus_client.start_http_server()` starts a metrics endpoint
4. Prometheus scrapes `http://host:8001/metrics`

This service emits **throughput metrics**, not storage metrics.

---

## 7. Instrumentation: quality service

### Files involved

```text
src/quality_service/
├── main.py
├── validator.py
└── repository.py
```

### Key responsibilities

- Increment `ticks_valid_total` / `ticks_invalid_total`
- Observe ingestion lag (`Histogram`)
- Track successful DB inserts
- Expose `/metrics` on a dedicated HTTP port

### How it works

1. Kafka consumer processes messages
2. Validation results drive metric updates
3. Lag is measured as:
   ```
   processing_time - event_time
   ```
4. Inserts into Postgres increment insert counters

This service emits **quality, integrity, and latency metrics**.

---

## 8. Prometheus configuration

Prometheus is configured via:

```text
infra/prometheus/prometheus.yml
```

Example scrape configuration:

```yaml
scrape_configs:
  - job_name: 'ingestion-service'
    static_configs:
      - targets: ['host.docker.internal:8001']

  - job_name: 'quality-service'
    static_configs:
      - targets: ['host.docker.internal:8002']
```

Key points:

- `host.docker.internal` allows Docker containers to reach host services
- Each service exposes metrics on a separate port
- Scrape interval is short (e.g. 5s) for near-real-time visibility

---

## 9. Docker integration

Prometheus and Grafana are added as services in:

```text
docker-compose.yml
```

This ensures:

- One-command startup of observability stack
- Consistent local environment
- Easy extension later (alerts, exporters)

---

## 10. Example PromQL queries

### Ingestion rate

```promql
sum(rate(ticks_produced_total[1m]))
```

### Validation rate

```promql
sum(rate(ticks_valid_total[1m]))
```

### Invalid tick rate (by reason)

```promql
sum by (reason)(rate(ticks_invalid_total[5m]))
```

### 95th percentile ingestion lag

```promql
histogram_quantile(
  0.95,
  sum by (le)(rate(ingestion_lag_seconds_bucket[5m]))
)
```

These queries correspond directly to code-level metrics.

---

## 11. What Phase 3 enables

With Phase 3 implemented, the team can now:

- Detect ingestion slowdowns
- Identify spikes in invalid data
- Monitor end-to-end latency
- Reason quantitatively about pipeline health

This phase lays the foundation for:

- Alerting
- SLOs
- Capacity planning

---

## 12. Design decisions and trade-offs

- Application-level metrics take priority over host metrics
- Simplicity preferred over large exporter stacks
- Prometheus chosen for pull-based, decoupled monitoring
- Grafana chosen for its ecosystem and flexibility

---

## 13. Phase 3 in context

Phase 3 complements earlier phases:

- Phase 1: data ingestion reliability
- Phase 2: data correctness & storage
- Phase 3: operational insight & trust

Together, these phases represent a **production-ready data foundation**.

---

## 14. Key takeaways

- Observability must be designed, not bolted on
- Metrics live in code, not in dashboards
- Grafana visualizes; Prometheus stores and queries
- Healthy pipelines are understood pipelines

Phase 3 elevates the project from *working system* to
**operable system**.
