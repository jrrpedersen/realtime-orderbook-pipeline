# This will connect to Kafka and publish ticks
import asyncio
from typing import AsyncIterator

from aiokafka import AIOKafkaProducer
from common.models import OrderBookTick

KAFKA_TOPIC = "orderbook.raw"


async def run_producer(
    bootstrap_servers: str,
    tick_stream: AsyncIterator[OrderBookTick],
) -> None:
    """
    Read ticks from an async generator and send them to Kafka.
    """
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
    await producer.start()
    try:
        async for tick in tick_stream:
            # serialize to JSON string using Pydantic's built-in method
            payload = tick.model_dump_json().encode("utf-8")

            print("Sending tick:", tick.model_dump())  # Phase 1: visible feedback

            await producer.send_and_wait(
                KAFKA_TOPIC,
                value=payload,
                key=tick.symbol.encode("utf-8"),
            )
    finally:
        await producer.stop()