# src/quality_service/parquet_writer.py

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from common.models import OrderBookTick

# Default to ../data/lake from this file, override via COLD_STORAGE_PATH
_DEFAULT_BASE = Path(__file__).resolve().parents[2] / "data" / "lake"
BASE_PATH = Path(os.getenv("COLD_STORAGE_PATH", str(_DEFAULT_BASE)))


def write_tick_to_parquet(tick: OrderBookTick) -> None:
    """
    Write a single validated tick to a partitioned Parquet file.

    Layout:
      data/lake/
        symbol=TTF-GAS/
          date=YYYY-MM-DD/
            <sequence_id>.parquet
    """
    date_str = tick.event_time.date().isoformat()

    dest_dir = BASE_PATH / f"symbol={tick.symbol}" / f"date={date_str}"
    dest_dir.mkdir(parents=True, exist_ok=True)

    file_path = dest_dir / f"{tick.sequence_id}.parquet"

    #print(f"[PARQUET] Writing tick -> {file_path}")

    df = pd.DataFrame([tick.model_dump()])
    # Small files are fine for this demo; in a real system you'd batch.
    df.to_parquet(file_path, index=False, engine="pyarrow")