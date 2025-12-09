import os

# Kafka broker address
# - from host: localhost:9092
# - from containers: kafka:9092 (but we only need localhost for now)
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")

# Postgres connection string
DB_DSN = os.getenv(
    "DB_DSN",
    "postgresql://market:market@localhost:5432/marketdata",
)