from typing import Tuple, Optional, Dict, Any

from common.models import OrderBookTick


def validate_tick(raw: Dict[str, Any]) -> Tuple[Optional[OrderBookTick], Optional[str]]:
    """
    Validate a raw dict from Kafka.

    Returns:
      (tick, None) if valid
      (None, error_message) if invalid
    """
    try:
        tick = OrderBookTick(**raw)
    except Exception as e:
        return None, f"schema_error: {e}"

    # Simple integrity check: bid must be strictly less than ask
    if tick.bid_price >= tick.ask_price:
        return None, "integrity_error: bid_price >= ask_price"

    # You can add more rules later (e.g. timeliness, volume ranges, etc.)
    return tick, None