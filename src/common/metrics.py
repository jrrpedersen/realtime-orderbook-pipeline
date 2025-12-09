# src/common/metrics.py
from prometheus_client import Counter, Histogram

# Ingestion metrics
ticks_produced_total = Counter(
    "ticks_produced_total",
    "Total number of ticks produced",
    ["service", "symbol"],
)

# Validation metrics
ticks_valid_total = Counter(
    "ticks_valid_total",
    "Total number of valid ticks processed",
    ["service", "symbol"],
)

ticks_invalid_total = Counter(
    "ticks_invalid_total",
    "Total number of invalid ticks rejected",
    ["service", "symbol", "reason"],
)

# DB insert metrics
db_inserts_total = Counter(
    "db_inserts_total",
    "Total number of rows inserted into the ticks table",
    ["service", "symbol"],
)

# End-to-end lag (event_time -> processed time)
ingestion_lag_seconds = Histogram(
    "ingestion_lag_seconds",
    "Lag in seconds between event_time and processing time",
    ["service", "symbol"],
)