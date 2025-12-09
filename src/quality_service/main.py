# simple Kafka consumer → validator → Postgres writer
import asyncio
import json

from aiokafka import AIOKafkaConsumer

from common.config import KAFKA_BROKER
from quality_service.validator import validate_tick
from quality_service.repository import init_db_pool, insert_tick


KAFKA_TOPIC = "orderbook.raw"


async def main() -> None:
    print(f"Connecting to Kafka at {KAFKA_BROKER}")
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id="quality-service",
        enable_auto_commit=True,
        auto_offset_reset="earliest",  # start from beginning if no committed offset
    )

    pool = await init_db_pool()
    await consumer.start()
    print("Quality service started. Consuming ticks...")

    try:
        async for msg in consumer:
            try:
                raw = json.loads(msg.value)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e} | raw={msg.value!r}")
                continue

            tick, err = validate_tick(raw)
            if err is not None:
                print(f"Invalid tick ({err}): {raw}")
                continue

            await insert_tick(pool, tick)
    finally:
        print("Shutting down quality service...")
        await consumer.stop()
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())