# src/data_audit/audit_parquet.py

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import great_expectations as gx

from great_expectations.dataset import PandasDataset

import os

_DEFAULT_BASE = Path(__file__).resolve().parents[2] / "data" / "lake"
BASE_PATH = Path(os.getenv("COLD_STORAGE_PATH", str(_DEFAULT_BASE)))


def load_parquet_partition(base_path: Path, symbol: str, date: str) -> pd.DataFrame:
    """
    Load all Parquet files for a given symbol and date
    from a partitioned 'data lake' layout:

      base_path/symbol=SYMBOL/date=YYYY-MM-DD/*.parquet
    """
    partition_dir = base_path / f"symbol={symbol}" / f"date={date}"
    if not partition_dir.exists():
        raise SystemExit(f"Partition directory not found: {partition_dir}")

    files = sorted(partition_dir.glob("*.parquet"))
    if not files:
        raise SystemExit(f"No parquet files found in {partition_dir}")

    dfs = [pd.read_parquet(f) for f in files]
    return pd.concat(dfs, ignore_index=True)


def run_expectations(df: pd.DataFrame) -> None:
    ge_df = PandasDataset(df)
    results = []

    results.append(
        ge_df.expect_column_values_to_not_be_null("symbol")
    )

    results.append(
        ge_df.expect_column_values_to_be_between(
            "bid_price", min_value=0
        )
    )

    results.append(
        ge_df.expect_column_values_to_be_between(
            "ask_price", min_value=0
        )
    )


    results.append(
        ge_df.expect_column_values_to_not_be_null(
            "event_time"
        )
    )

    print("\nGreat Expectations summary:")
    all_success = True
    for r in results:
        et = r["expectation_config"]["expectation_type"]
        ok = r["success"]
        print(f"  {et}: {'✅' if ok else '❌'}")
        if not ok:
            all_success = False

    print(f"\nOverall success: {all_success}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument(
        "--base-path",
        default=str(Path(__file__).resolve().parents[2] / "data" / "lake"),
        help="Base path of the Parquet data lake (default: ../data/lake)",
    )
    args = parser.parse_args()

    print(f"Loading Parquet data for symbol={args.symbol}, date={args.date}")

    df = load_parquet_partition(
        base_path=Path(args.base_path),
        symbol=args.symbol,
        date=args.date,
    )

    print(f"Loaded {len(df)} rows")

    run_expectations(df)


if __name__ == "__main__":
    main()