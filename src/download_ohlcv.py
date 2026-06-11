from typing import List, Union, Dict, Optional
import time

import ccxt
import pandas as pd
from loguru import logger
from ccxt.base.exchange import Exchange


class CryptoPriceDataService:
    """
    Service for downloading OHLCV crypto price data from multiple exchanges
    using the ccxt library.

    The output is a cleaned pandas DataFrame with datetime index and
    standardized OHLCV column names.
    """

    TIMEFRAME_MS: Dict[str, int] = {
        "1d": 86400000,
        "1h": 3600000,
        "30m": 1800000,
        "15m": 900000,
        "5m": 300000,
        "1m": 60000,
    }

    OHLCV_COLUMNS: List[str] = ["open", "high", "low", "close", "volume"]

    exchange_dict: Dict[str, Exchange] = {
        "binance": ccxt.binance(),
        "binanceusdm": ccxt.binanceusdm(),
        "kucoin": ccxt.kucoin(),
        "huobi": ccxt.huobi(),
        "lbank": ccxt.lbank(),
    }

    @classmethod
    def fetch_ohlcv_time_series_df(
        cls,
        symbol: str = "BTC/USDT",
        exchange_name: str = "binance",
        timeframe: str = "1d",
        date_since: str = "2023-01-01T00:00:00Z",
        limit: int = 1000,
    ) -> Optional[pd.DataFrame]:
        """
        Download historical OHLCV data from a selected exchange.

        Parameters
        ----------
        symbol : str
            Trading pair, e.g. "BTC/USDT".
        exchange_name : str
            Exchange name supported in exchange_dict.
        timeframe : str
            Candle timeframe, e.g. "1d", "1h", "15m".
        date_since : str
            Start date in ISO8601 format.
        limit : int
            Number of candles per API request.

        Returns
        -------
        Optional[pd.DataFrame]
            DataFrame indexed by timestamp with OHLCV columns.
        """

        exchange: Optional[Exchange] = cls.exchange_dict.get(exchange_name)

        if exchange is None:
            logger.error("Input exchange is not available: {}", exchange_name)
            return None

        if timeframe not in cls.TIMEFRAME_MS:
            logger.error("Unsupported timeframe: {}", timeframe)
            return None

        timestamp_since: int = exchange.parse8601(date_since)

        logger.info(
            "Start downloading OHLCV data: exchange={}, symbol={}, timeframe={}, since={}",
            exchange_name,
            symbol,
            timeframe,
            date_since,
        )

        all_candles: List[List[Union[int, float]]] = exchange.fetch_ohlcv(
            symbol,
            timeframe,
            since=timestamp_since,
            limit=limit,
        )

        if len(all_candles) == 0:
            logger.error("No data returned. Please check symbol or start date.")
            return None

        last_timestamp: int = all_candles[-1][0]
        timeframe_ms: int = cls.TIMEFRAME_MS[timeframe]

        while exchange.milliseconds() - last_timestamp >= timeframe_ms:
            time.sleep(exchange.rateLimit / 1000)

            next_timestamp: int = last_timestamp + timeframe_ms

            candles: List[List[Union[int, float]]] = exchange.fetch_ohlcv(
                symbol,
                timeframe,
                since=next_timestamp,
                limit=limit,
            )

            # Handle exchange maintenance or missing data periods
            while len(candles) == 0:
                logger.warning("Empty response at timestamp: {}", next_timestamp)
                time.sleep(exchange.rateLimit / 1000)
                next_timestamp += timeframe_ms

                candles = exchange.fetch_ohlcv(
                    symbol,
                    timeframe,
                    since=next_timestamp,
                    limit=limit,
                )

            all_candles.extend(candles)
            last_timestamp = all_candles[-1][0]

            logger.info(
                "Fetched up to timestamp: {}",
                exchange.iso8601(last_timestamp),
            )

        df: pd.DataFrame = pd.DataFrame.from_records(
            all_candles,
            columns=["timestamp_ms"] + cls.OHLCV_COLUMNS,
        )

        df["timestamp"] = pd.to_datetime(df["timestamp_ms"], unit="ms", utc=True)

        df = df.drop(columns=["timestamp_ms"])
        df = df.drop_duplicates(subset=["timestamp"])
        df = df.sort_values("timestamp")
        df = df.set_index("timestamp")

        return df


if __name__ == "__main__":
    df = CryptoPriceDataService.fetch_ohlcv_time_series_df(
        symbol="BTC/USDT",
        exchange_name="binance",
        timeframe="1d",
        date_since="2023-01-01T00:00:00Z",
    )

    if df is not None:
        output_path = "BTC_USDT_binance_1d.csv"
        df.to_csv(output_path)
        logger.info("Data saved to {}", output_path)
        print(df.head())
        print(df.tail())
