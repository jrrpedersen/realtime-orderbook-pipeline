from datetime import datetime
from pydantic import BaseModel, Field


class OrderBookTick(BaseModel):
    """
    Minimal representation of an orderbook 'tick' for a single symbol.

    Phase 1: keep it simple: top-of-book only (best bid/ask).
    """

    symbol: str
    event_time: datetime
    received_time: datetime
    bid_price: float = Field(gt=0)
    ask_price: float = Field(gt=0)
    bid_volume: float = Field(ge=0)
    ask_volume: float = Field(ge=0)
    sequence_id: int = Field(ge=0)