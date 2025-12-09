# This will connect to Kafka and publish ticks
# src/ingestion_service/producer.py
import asyncio
from typing import AsyncIterator

from aiokafka import AIOKafkaProducer
from common.models import OrderBookTick
from common.metrics import ticks_produced_total

KAFKA_TOPIC = "orderbook.raw"


async def run_producer(
    bootstrap_servers: str,
    tick_stream: AsyncIterator[OrderBookTick],
    service_name: str = "ingestion-service",
) -> None:
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
    await producer.start()
    try:
        async for tick in tick_stream:
            payload = tick.model_dump_json().encode("utf-8")

            print("Sending tick:", tick.model_dump())

            # metrics
            ticks_produced_total.labels(
                service=service_name,
                symbol=tick.symbol,
            ).inc()

            await producer.send_and_wait(
                KAFKA_TOPIC,
                value=payload,
                key=tick.symbol.encode("utf-8"),
            )
    finally:
        await producer.stop()