import asyncpg
from common.config import DB_DSN
from common.models import OrderBookTick


async def init_db_pool():
    """
    Create an async connection pool to Postgres.
    """
    return await asyncpg.create_pool(dsn=DB_DSN)


async def insert_tick(pool, tick: OrderBookTick) -> None:
    """
    Insert a validated tick into the ticks table.
    """
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO ticks (
                symbol,
                event_time,
                received_time,
                bid_price,
                ask_price,
                bid_volume,
                ask_volume,
                sequence_id
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
            """,
            tick.symbol,
            tick.event_time,
            tick.received_time,
            tick.bid_price,
            tick.ask_price,
            tick.bid_volume,
            tick.ask_volume,
            tick.sequence_id,
        )