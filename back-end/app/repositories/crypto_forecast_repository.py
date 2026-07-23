from typing import Optional

import pandas as pd
from app.clients.supabase_client import get_supabase_client
from app.services.binance_market_data_service import BinanceMarketService


class CryptoForecastRepository:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.binance_service = BinanceMarketService()

    def save_ticker_24hr(self):
        """
        Salva os dados de ticker de 24 horas no Supabase.
        Returns:
            dict: Resposta da operação de salvamento no Supabase.
        """
        df = self.binance_service.get_ticker_24hr()
        if df.empty:
            return
        else:
            df_prep = df.copy()
            df_prep = df_prep.rename(
                columns={
                    "symbol": "symbol",
                    "priceChange": "price_change",
                    "priceChangePercent": "price_change_percent",
                    "weightedAvgPrice": "weighted_avg_price",
                    "prevClosePrice": "prev_close_price",
                    "lastPrice": "last_price",
                    "lastQty": "last_qty",
                    "bidPrice": "bid_price",
                    "bidQty": "bid_qty",
                    "askPrice": "ask_price",
                    "askQty": "ask_qty",
                    "openPrice": "open_price",
                    "highPrice": "high_price",
                    "lowPrice": "low_price",
                    "volume": "volume",
                    "quoteVolume": "quote_volume",
                    "openTime": "open_time",
                    "closeTime": "close_time",
                    "firstId": "first_id",
                    "lastId": "last_id",
                    "count": "count",
                }
            )

            if "open_time" in df_prep.columns:
                df_prep["open_time"] = df_prep["open_time"].dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            if "close_time" in df_prep.columns:
                df_prep["close_time"] = df_prep["close_time"].dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            dados_para_salvar = df_prep.to_dict(orient="records")
            try:
                response = (
                    self.supabase.table("ticker_24hr_history")
                    .upsert(dados_para_salvar, on_conflict="symbol,open_time")
                    .execute()
                )
                print(
                    f"Sucesso! {len(dados_para_salvar)} registros de tickers salvos/atualizados no Supabase."
                )
                return response

            except Exception as e:
                print(f"Erro ao salvar os tickers de 24h no Supabase: {e}")
                return None

    def save_orderbook_tickers(self):
        """
        Salva os dados de orderbook tickers no Supabase.
        Returns:
            dict: Resposta da operação de salvamento no Supabase.
        """
        df = self.binance_service.get_orderbook_tickers()
        if df.empty:
            return
        else:
            df_prep = df.copy()
            df_prep = df_prep.rename(
                columns={
                    "symbol": "symbol",
                    "bidPrice": "bid_price",
                    "bidQty": "bid_qty",
                    "askPrice": "ask_price",
                    "askQty": "ask_qty",
                }
            )
            df_prep["fetched_at"] = pd.Timestamp.now(tz="UTC").strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            dados_para_salvar = df_prep.to_dict(orient="records")
            try:
                response = (
                    self.supabase.table("orderbook_tickers")
                    .upsert(dados_para_salvar, on_conflict="symbol,fetched_at")
                    .execute()
                )
                print(
                    f"Sucesso! {len(dados_para_salvar)} registros de orderbook salvos/atualizados no Supabase."
                )
                return response
            except Exception as e:
                print(f"Erro ao salvar os orderbook no Supabase: {e}")
                return None

    def save_klines(self, interval: str, start_str: Optional[str] = None):
        """
        Salva os dados de klines no Supabase para o intervalo especificado.
        Se start_str for informado, usa get_historical_klines (backfill).
        Args:
            interval: Intervalo (ex: '15m', '1h', '1d')
            start_str: Data inicial para backfill (ex: '30 days ago UTC')
        Returns:
            dict: Resposta da operação de salvamento no Supabase.
        """
        if start_str:
            df = self.binance_service.get_historical_klines(interval, start_str)
        else:
            df = self.binance_service.get_klines(interval)
        if df.empty:
            return
        else:
            df_prep = df.copy()
            df_prep = df_prep.rename(
                columns={
                    "symbol": "symbol",
                    "Open_Time": "open_time",
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume",
                    "Close_Time": "close_time",
                    "Quote_Asset_Volume": "quote_asset_volume",
                    "Number_of_Trades": "number_of_trades",
                    "Taker_Buy_Base_Asset_Volume": "taker_buy_base_asset_volume",
                    "Taker_Buy_Quote_Asset_Volume": "taker_buy_quote_asset_volume",
                }
            )
            if "interval" in df_prep.columns:
                df_prep = df_prep.drop(columns=["interval"])
            if "open_time" in df_prep.columns:
                df_prep["open_time"] = df_prep["open_time"].dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            if "close_time" in df_prep.columns:
                df_prep["close_time"] = df_prep["close_time"].dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            dados_para_salvar = df_prep.to_dict(orient="records")
            batch_size = 200
            total = len(dados_para_salvar)
            for i in range(0, total, batch_size):
                batch = dados_para_salvar[i : i + batch_size]
                try:
                    self.supabase.table(f"klines_{interval}").upsert(
                        batch, on_conflict="symbol,open_time"
                    ).execute()
                    print(
                        f"Lote {i // batch_size + 1}/{(total - 1) // batch_size + 1}: "
                        f"{len(batch)} registros de klines salvos/atualizados no Supabase."
                    )
                except Exception as e:
                    print(f"Erro ao salvar lote de klines no Supabase: {e}")
            print(f"Total: {total} registros de klines processados.")
            return {"status": "processed", "total": total}


