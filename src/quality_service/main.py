# src/quality_service/main.py
import asyncio
import json
import os
from datetime import datetime, timezone

from aiokafka import AIOKafkaConsumer
from prometheus_client import start_http_server

from common.models import OrderBookTick
from common.metrics import (
    ticks_valid_total,
    ticks_invalid_total,
    db_inserts_total,
    ingestion_lag_seconds,
)
from quality_service.repository import init_db_pool, insert_tick

from quality_service.parquet_writer import write_tick_to_parquet


KAFKA_TOPIC = "orderbook.raw"
CONSUMER_GROUP = "quality-service"


def get_kafka_bootstrap_servers() -> str:
    return os.getenv("KAFKA_BROKER", "localhost:9092")


async def consume_and_validate() -> None:
    bootstrap_servers = get_kafka_bootstrap_servers()
    print(f"Connecting to Kafka at {bootstrap_servers}")

    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=bootstrap_servers,
        group_id=CONSUMER_GROUP,
        enable_auto_commit=True,
    )

    await consumer.start()
    pool = await init_db_pool()

    try:
        async for msg in consumer:
            try:
                raw = json.loads(msg.value)
                tick = OrderBookTick(**raw)
            except Exception as e:
                # schema or JSON error
                ticks_invalid_total.labels(
                    service="quality-service",
                    symbol=raw.get("symbol", "UNKNOWN") if isinstance(raw, dict) else "UNKNOWN",
                    reason=type(e).__name__,
                ).inc()
                continue

            # domain check: bid < ask
            if not (tick.bid_price < tick.ask_price):
                ticks_invalid_total.labels(
                    service="quality-service",
                    symbol=tick.symbol,
                    reason="bid_not_less_than_ask",
                ).inc()
                continue

            # metrics: valid tick
            ticks_valid_total.labels(
                service="quality-service",
                symbol=tick.symbol,
            ).inc()

            # lag metric
            now = datetime.now(timezone.utc)
            lag = (now - tick.event_time).total_seconds()
            ingestion_lag_seconds.labels(
                service="quality-service",
                symbol=tick.symbol,
            ).observe(lag)

            # insert into DB
            await insert_tick(pool, tick)
            db_inserts_total.labels(
                service="quality-service",
                symbol=tick.symbol,
            ).inc()
            # write to Parquet (cold store)
            write_tick_to_parquet(tick)

    finally:
        await consumer.stop()
        await pool.close()


async def main() -> None:
    await consume_and_validate()


if __name__ == "__main__":
    metrics_port = int(os.getenv("METRICS_PORT", "8002"))
    print(f"Starting quality-service metrics server on port {metrics_port}")
    start_http_server(metrics_port)

    asyncio.run(main())