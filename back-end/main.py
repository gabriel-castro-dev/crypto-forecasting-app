from app.services.binance_market_data_service import BinanceMarketService

service = BinanceMarketService()

print(service.ping())
