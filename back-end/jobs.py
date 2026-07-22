import sys

from app.repositories.crypto_forecast_repository import CryptoForecastRepository


def main():
    repo = CryptoForecastRepository()
    job_type = sys.argv[1] if len(sys.argv) > 1 else "hourly"

    if job_type == "hourly":
        repo.save_ticker_24hr()
        # repo.save_klines_1h()
    # elif job_type == "daily":
    # repo.save_klines_1d()


if __name__ == "__main__":
    main()
