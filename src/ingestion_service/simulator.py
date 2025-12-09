import asyncio
import random
from datetime import datetime, timezone
from typing import AsyncIterator

from common.models import OrderBookTick


class PriceSimulator:
    """
    Simple random-walk price simulator for a single symbol.

    - price moves randomly in small steps
    - bid/ask are set with a fixed spread around mid price
    - sequence_id increments per tick
    """

    def __init__(self, symbol: str, start_price: float = 100.0, tick_interval: float = 0.05):
        self.symbol = symbol
        self.price = start_price
        self.tick_interval = tick_interval  # seconds between ticks
        self.sequence_id = 0

    async def stream(self, max_ticks: int | None = None) -> AsyncIterator[OrderBookTick]:
        """
        Asynchronously yield OrderBookTick objects.

        If max_ticks is None, runs forever; otherwise stops after max_ticks.
        """
        count = 0
        while max_ticks is None or count < max_ticks:
            count += 1
            self.sequence_id += 1

            # basic random walk
            self.price += random.uniform(-0.1, 0.1)
            spread = 0.01
            bid = self.price - spread / 2
            ask = self.price + spread / 2

            now = datetime.now(timezone.utc)

            yield OrderBookTick(
                symbol=self.symbol,
                event_time=now,
                received_time=now,
                bid_price=bid,
                ask_price=ask,
                bid_volume=random.uniform(1, 100),
                ask_volume=random.uniform(1, 100),
                sequence_id=self.sequence_id,
            )

            await asyncio.sleep(self.tick_interval)