import sys

from app.repositories.crypto_forecast_repository import CryptoForecastRepository


def main():
    repo = CryptoForecastRepository()
    job_type = sys.argv[1] if len(sys.argv) > 1 else "hourly"

    if job_type == "five-minutes":
        repo.save_orderbook_tickers()
    elif job_type == "hourly":
        repo.save_ticker_24hr()
    elif job_type == "daily":
        repo.save_klines("15m")
        repo.save_klines("1h")
        repo.save_klines("1d")


if __name__ == "__main__":
    main()
