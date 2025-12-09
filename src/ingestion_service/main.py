# src/ingestion_service/main.py
import asyncio
import os

from prometheus_client import start_http_server

from ingestion_service.simulator import PriceSimulator
from ingestion_service.producer import run_producer


def get_kafka_bootstrap_servers() -> str:
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

    await run_producer(
        bootstrap_servers=bootstrap_servers,
        tick_stream=stream,
        service_name="ingestion-service",
    )


if __name__ == "__main__":
    # Start metrics HTTP server on configurable port
    metrics_port = int(os.getenv("METRICS_PORT", "8001"))
    print(f"Starting ingestion metrics server on port {metrics_port}")
    start_http_server(metrics_port)

    asyncio.run(main())