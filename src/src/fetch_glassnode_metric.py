from typing import Optional
import os

import pandas as pd
import requests
from dotenv import load_dotenv
from loguru import logger


load_dotenv()

GLASSNODE_API_KEY = os.getenv("GLASSNODE_API_KEY")
GLASSNODE_BASE_URL = "https://glassnode-quant-proxy.gemini-acc.workers.dev/v1/metrics"


def parse_to_unix_timestamp(date_string: Optional[str]) -> Optional[int]:
    """
    Convert a date string into a Unix timestamp in seconds.
    """

    if date_string is None:
        return None

    dt = pd.to_datetime(date_string, utc=True)
    return int(dt.timestamp())


def fetch_glassnode_metric(
    metric_path: str,
    asset: str = "BTC",
    interval: str = "24h",
    since: Optional[str] = None,
    output_path: Optional[str] = None,
) -> pd.DataFrame:
    """
    Fetch a Glassnode on-chain metric and return it as a pandas DataFrame.

    Parameters
    ----------
    metric_path : str
        Glassnode metric path, for example: addresses/active_count
    asset : str
        Asset ticker, for example: BTC or ETH
    interval : str
        Data interval, for example: 24h
    since : Optional[str]
        Optional start date, for example: 2023-01-01
    output_path : Optional[str]
        Optional CSV output path

    Returns
    -------
    pd.DataFrame
        DataFrame with timestamp and value columns.
    """

    if not GLASSNODE_API_KEY:
        raise EnvironmentError(
            "GLASSNODE_API_KEY is missing. Please create a .env file based on .env.example."
        )

    if not metric_path.startswith("/"):
        metric_path = "/" + metric_path

    url = GLASSNODE_BASE_URL + metric_path

    params = {
        "a": asset,
        "i": interval,
    }

    since_ts = parse_to_unix_timestamp(since)

    if since_ts is not None:
        params["s"] = since_ts

    headers = {
        "Authorization": f"Bearer {GLASSNODE_API_KEY}",
    }

    logger.info(
        "Fetching Glassnode metric={} asset={} interval={}",
        metric_path,
        asset,
        interval,
    )

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data)

    if df.empty:
        return pd.DataFrame(columns=["timestamp", "value"])

    df["timestamp"] = pd.to_datetime(df["t"], unit="s", utc=True)
    df = df.rename(columns={"v": "value"})
    df = df[["timestamp", "value"]]
    df = df.sort_values("timestamp").reset_index(drop=True)

    if output_path:
        df.to_csv(output_path, index=False)
        logger.info("Saved Glassnode data to {}", output_path)

    return df


if __name__ == "__main__":
    df = fetch_glassnode_metric(
        metric_path="addresses/active_count",
        asset="BTC",
        interval="24h",
        since="2023-01-01",
        output_path="outputs/glassnode_btc_active_addresses.csv",
    )

    print(df.head())
