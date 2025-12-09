import asyncio
import os

from ingestion_service.simulator import PriceSimulator
from ingestion_service.producer import run_producer


def get_kafka_bootstrap_servers() -> str:
    # In Docker Compose, use 'kafka:9092'.
    # Expose it as localhost:9092.
    return os.getenv("KAFKA_BROKER", "localhost:9092")


async def main() -> None:
    symbol = os.getenv("SYMBOL", "TTF-GAS")
    tick_interval = float(os.getenv("TICK_INTERVAL", "0.05"))
    max_ticks_str = os.getenv("MAX_TICKS", "")
    max_ticks = int(max_ticks_str) if max_ticks_str else None

    sim = PriceSimulator(symbol=symbol, tick_interval=tick_interval)
    stream = sim.stream(max_ticks=max_ticks)

    bootstrap_servers = get_kafka_bootstrap_servers()
    print(f"Connecting to Kafka at {bootstrap_servers}")
    print(f"Producing ticks for symbol '{symbol}' every {tick_interval} seconds")

    await run_producer(bootstrap_servers=bootstrap_servers, tick_stream=stream)


if __name__ == "__main__":
    asyncio.run(main())