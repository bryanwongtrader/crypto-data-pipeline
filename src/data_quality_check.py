from pathlib import Path
from typing import Dict, Any

import pandas as pd
from loguru import logger


def load_ohlcv_csv(file_path: str) -> pd.DataFrame:
    """
    Load an OHLCV CSV file and parse timestamp column.

    Parameters
    ----------
    file_path : str
        Path to the OHLCV CSV file.

    Returns
    -------
    pd.DataFrame
        Loaded OHLCV dataframe.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(path)

    if "timestamp" not in df.columns:
        raise ValueError("CSV must contain a 'timestamp' column.")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp").reset_index(drop=True)

    return df


def check_required_columns(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Check whether all required OHLCV columns exist.
    """

    required_columns = ["timestamp", "open", "high", "low", "close", "volume"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    return {
        "check": "required_columns",
        "passed": len(missing_columns) == 0,
        "missing_columns": missing_columns,
    }


def check_missing_values(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Check missing values in each column.
    """

    missing_values = df.isna().sum().to_dict()
    total_missing = int(df.isna().sum().sum())

    return {
        "check": "missing_values",
        "passed": total_missing == 0,
        "total_missing": total_missing,
        "missing_by_column": missing_values,
    }


def check_duplicate_timestamps(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Check duplicated timestamps.
    """

    duplicated_count = int(df["timestamp"].duplicated().sum())

    return {
        "check": "duplicate_timestamps",
        "passed": duplicated_count == 0,
        "duplicated_count": duplicated_count,
    }


def check_chronological_order(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Check whether timestamps are sorted in increasing order.
    """

    is_sorted = bool(df["timestamp"].is_monotonic_increasing)

    return {
        "check": "chronological_order",
        "passed": is_sorted,
    }


def check_ohlc_logic(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Check whether OHLC prices are internally consistent.

    Conditions:
    - high should be greater than or equal to open, low, and close
    - low should be less than or equal to open, high, and close
    """

    invalid_high = df[
        (df["high"] < df["open"])
        | (df["high"] < df["low"])
        | (df["high"] < df["close"])
    ]

    invalid_low = df[
        (df["low"] > df["open"])
        | (df["low"] > df["high"])
        | (df["low"] > df["close"])
    ]

    invalid_count = int(len(invalid_high) + len(invalid_low))

    return {
        "check": "ohlc_logic",
        "passed": invalid_count == 0,
        "invalid_high_count": int(len(invalid_high)),
        "invalid_low_count": int(len(invalid_low)),
    }


def check_volume(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Check whether volume contains negative values.
    """

    negative_volume_count = int((df["volume"] < 0).sum())

    return {
        "check": "volume",
        "passed": negative_volume_count == 0,
        "negative_volume_count": negative_volume_count,
    }


def calculate_return_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate simple close-to-close return summary.
    """

    df = df.copy()
    df["return"] = df["close"].pct_change()

    return {
        "check": "return_summary",
        "row_count": int(len(df)),
        "start_timestamp": str(df["timestamp"].min()),
        "end_timestamp": str(df["timestamp"].max()),
        "mean_return": float(df["return"].mean()),
        "return_volatility": float(df["return"].std()),
        "min_return": float(df["return"].min()),
        "max_return": float(df["return"].max()),
    }


def run_data_quality_check(file_path: str) -> None:
    """
    Run all data quality checks and print the results.
    """

    logger.info("Loading OHLCV data from {}", file_path)
    df = load_ohlcv_csv(file_path)

    checks = [
        check_required_columns(df),
        check_missing_values(df),
        check_duplicate_timestamps(df),
        check_chronological_order(df),
        check_ohlc_logic(df),
        check_volume(df),
        calculate_return_summary(df),
    ]

    logger.info("Data quality check completed.")

    for result in checks:
        print(result)


if __name__ == "__main__":
    sample_file = "data_sample/BTC_USDT_binance_1d_sample.csv"
    run_data_quality_check(sample_file)
