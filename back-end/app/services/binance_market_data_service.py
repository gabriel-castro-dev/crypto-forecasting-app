import logging
from typing import Optional

import pandas as pd
from app.clients.binance_client import BinanceClient

logger = logging.getLogger(__name__)


class BinanceMarketService:
    """
    Serviço responsável por requisições e transformação de dados de mercado na API Binance.

    Encapsula todas as transformações dos dados provenientes da API Binance, incluindo:
    - Retry logic com validação de conectividade
    - Transformação de dados brutos em DataFrames estruturados
    - Type casting apropriado (int, float, datetime)
    - Validação de dados e tratamento de erros específicos

    Attributes:
        client: Classe BinanceClient já autenticada para requisições de dados de mercado
    """

    def __init__(self) -> None:
        """
        Inicializa o serviço de dados de mercado.

        Raises:
            RuntimeError: Se não conseguir conectar à API Binance
        """
        try:
            self.client = BinanceClient()
            logger.info("BinanceMarketService inicializado com sucesso")
        except Exception as e:
            logger.error("Falha crítica ao iniciar cliente Binance")
            raise RuntimeError(f"{e}")

    def ping(self) -> str:
        """
        Verifica conectividade com a API Binance.

        Returns:
            Mensagem indicando status da conexão
        """
        resultado = self.client.ping()
        if resultado:
            return "Binance API is reachable."

        return "Error pinging Binance API"

    def server_time(self) -> dict:
        """
        Obtém o horário atual do servidor Binance.

        Returns:
            Dict com timestamp ou mensagem de erro
        """
        result = self.client.server_time()

        if result is None:
            return {
                "status": "error",
                "message": "Não foi possível obter o horário do servidor.",
            }

        return result

    def system_status(self) -> dict:
        """
        Obtém status do sistema Binance.

        Returns:
            Dict com status ou mensagem de erro
        """
        result = self.client.system_status()

        if result is None:
            return {
                "status": "error",
                "message": "Não foi possível obter o status do sistema.",
            }

        return result

    def get_tickers(self) -> pd.DataFrame:
        """
        Obtém lista de todos os tickers com pares USDT, ordenados por preço.

        Returns:
            DataFrame com tickers USDT ordenados ou DataFrame vazio se falhar
        """
        data = self.client.get_tickers()
        if data:
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                usdt_tickers = df[df["symbol"].str.endswith("USDT")].copy()
                usdt_tickers["price"] = pd.to_numeric(
                    usdt_tickers["price"], errors="coerce"
                )
                usdt_tickers["price"] = usdt_tickers["price"].round(2)
                usdt_tickers = usdt_tickers.dropna(subset=["price"])
                usdt_tickers = usdt_tickers.sort_values(
                    by="price", ascending=False
                ).reset_index(drop=True)
                logger.info(f"Obtidos {len(usdt_tickers)} tickers USDT")
                return usdt_tickers
        else:
            logger.error("Falha ao transformar tickers")
            return pd.DataFrame()

    def get_ticker_24hr(self) -> pd.DataFrame:
        """
        Obtém dados de 24h dos pares USDT.

        Returns:
            DataFrame com dados 24h ou DataFrame vazio se falhar
        """
        df_tickers = self.get_tickers()
        symbols = df_tickers["symbol"].tolist()
        all_data = []

        if not df_tickers.empty:
            for symbol in symbols:
                data = self.client.get_ticker_24hr(symbol=symbol)
                if isinstance(data, dict) and data:
                    all_data.append(data)

            if all_data:
                df = pd.DataFrame(all_data)
                ignorar_colunas = [
                    "symbol",
                    "openTime",
                    "closeTime",
                    "firstId",
                    "lastId",
                    "count",
                ]
                cols_to_numeric = [
                    col for col in df.columns if col not in ignorar_colunas
                ]
                df[cols_to_numeric] = df[cols_to_numeric].apply(
                    pd.to_numeric, errors="coerce"
                )
                df[cols_to_numeric] = df[cols_to_numeric].round(8)
                df = df.dropna(subset=cols_to_numeric)
                df["openTime"] = pd.to_datetime(df["openTime"], unit="ms")
                df["closeTime"] = pd.to_datetime(df["closeTime"], unit="ms")
                df[["symbol", "firstId", "lastId"]] = df[
                    ["symbol", "firstId", "lastId"]
                ].astype(str)
                df["count"] = df["count"].astype(int)
                logger.info(f"Dados 24h obtidos para {len(symbols)} símbolos")
                return df
            else:
                logger.error("Falha ao obter dados 24h para os tickers USDT")
                return pd.DataFrame()
        else:
            logger.error("Falha ao obter lista de tickers USDT")
            return pd.DataFrame()

    def get_top_20_tickers(self) -> pd.DataFrame:
        """
        Obtém os 20 principais tickers USDT com base no volume.

        Returns:
            DataFrame com os 20 principais tickers ou DataFrame vazio se falhar
        """
        df_tickers = self.get_ticker_24hr()
        if not df_tickers.empty:
            sorted_df = df_tickers.sort_values(by="quoteVolume", ascending=False)
            top_20 = sorted_df.head(20).reset_index(drop=True)
            logger.info("Obtidos os 20 principais tickers USDT")
            return top_20
        else:
            logger.error("Falha ao obter os 20 principais tickers USDT")
            return pd.DataFrame(columns=["symbol"])

    def get_orderbook_tickers(self) -> pd.DataFrame:
        """
        Obtém informações de order book dos top 20 pares USDT.

        Returns:
            DataFrame com dados de order book ou DataFrame vazio se falhar
        """

        df_tickers = self.get_top_20_tickers()
        symbols = df_tickers["symbol"].tolist()
        all_data = []

        if not df_tickers.empty:
            for symbol in symbols:
                data = self.client.get_orderbook_tickers(symbol=symbol)
                if isinstance(data, dict) and data:
                    all_data.append(data)
                    logger.info(f"Order book obtido para {symbol}")
                else:
                    logger.error(f"Falha ao obter order book para {symbol}")
        if all_data:
            df = pd.DataFrame(all_data)
            df["symbol"] = df["symbol"].astype(str)
            cols = ["bidPrice", "bidQty", "askPrice", "askQty"]

            df[cols] = df[cols].apply(pd.to_numeric, errors="coerce")
            df[cols] = df[cols].round(8)
            df = df.dropna(subset=cols)

            logger.info(f"Order book obtido para {len(symbols)} símbolos")
            return df
        else:
            logger.error(f"Falha ao obter order book para {len(symbols)} símbolos")
            return pd.DataFrame()

    def get_klines(self, interval: str) -> pd.DataFrame:
        """
        Obtém K-lines (velas) em tempo real de todos os top 20 pares USDT.

        Args:
            interval: Intervalo (ex: '1m', '1h', '1d')

        Returns:
            DataFrame com OHLCV ou DataFrame vazio se falhar
        """
        df_tickers = self.get_top_20_tickers()
        symbols = df_tickers["symbol"].tolist()
        all_data = []

        if not df_tickers.empty:
            for symbol in symbols:
                data = self.client.get_klines(symbol=symbol, interval=interval)
                if isinstance(data, list) and data:
                    for kline in data:
                        all_data.append(kline + [symbol])
                    logger.info(f"K-lines obtidas para {symbol} ({interval})")
                else:
                    logger.error(f"Falha ao obter k-lines para {symbol}")

        if all_data:
            columns = [
                "Open_Time",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "Close_Time",
                "Quote_Asset_Volume",
                "Number_of_Trades",
                "Taker_Buy_Base_Asset_Volume",
                "Taker_Buy_Quote_Asset_Volume",
                "Ignore",
                "symbol",
            ]
            df = pd.DataFrame(data=all_data, columns=columns)
            df = df.drop(columns=["Ignore"])
            df["Open_Time"] = pd.to_datetime(df["Open_Time"], unit="ms")
            df["Close_Time"] = pd.to_datetime(df["Close_Time"], unit="ms")
            df["Number_of_Trades"] = df["Number_of_Trades"].astype(int)

            numeric_cols = [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "Quote_Asset_Volume",
                "Taker_Buy_Base_Asset_Volume",
                "Taker_Buy_Quote_Asset_Volume",
            ]

            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
            df[numeric_cols] = df[numeric_cols].round(8)
            df = df.dropna(subset=numeric_cols)

            logger.info(
                f"Obtidas {len(df)} k-lines para {len(symbols)} símbolos ({interval})"
            )
            return df
        else:
            logger.error("Falha ao obter k-lines para os tickers USDT")
            return pd.DataFrame()

    def get_historical_klines(
        self,
        interval: str,
        start_str: str,
        end_str: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Obtém K-lines históricas de um período específico para todos os top 20 pares USDT.

        Args:
            interval: Intervalo (ex: '1h', '1d')
            start_str: Data inicial (ex: '10 days ago UTC')
            end_str: Data final (opcional)
            limit: Número máximo de registros

        Returns:
            DataFrame com k-lines históricas ou DataFrame vazio se falhar
        """
        df_tickers = self.get_top_20_tickers()
        symbols = df_tickers["symbol"].tolist()
        all_data = []

        if not df_tickers.empty:
            for symbol in symbols:
                data = self.client.get_historical_klines(
                    symbol=symbol,
                    interval=interval,
                    start_str=start_str,
                    end_str=end_str,
                    limit=limit,
                )
                if isinstance(data, list) and data:
                    for kline in data:
                        all_data.append(kline + [symbol])
                    logger.info(f"K-lines históricas obtidas para {symbol}")
                else:
                    logger.error(f"Falha ao obter k-lines históricas para {symbol}")

        if all_data:
            columns = [
                "Open_Time",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "Close_Time",
                "Quote_Asset_Volume",
                "Number_of_Trades",
                "Taker_Buy_Base_Asset_Volume",
                "Taker_Buy_Quote_Asset_Volume",
                "Ignore",
                "symbol",
            ]
            df = pd.DataFrame(data=all_data, columns=columns)
            df = df.drop(columns=["Ignore"])
            df["Open_Time"] = pd.to_datetime(df["Open_Time"], unit="ms").dt.strftime(
                "%d/%m/%Y %H:%M:%S"
            )
            df["Close_Time"] = pd.to_datetime(df["Close_Time"], unit="ms").dt.strftime(
                "%d/%m/%Y %H:%M:%S"
            )
            df["Number_of_Trades"] = df["Number_of_Trades"].astype(int)

            numeric_cols = [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "Quote_Asset_Volume",
                "Taker_Buy_Base_Asset_Volume",
                "Taker_Buy_Quote_Asset_Volume",
            ]

            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
            df[numeric_cols] = df[numeric_cols].round(8)
            df = df.dropna(subset=numeric_cols)

            logger.info(
                f"Obtidas {len(df)} k-lines históricas para {len(symbols)} símbolos"
            )
            return df
        else:
            logger.error("Falha ao obter k-lines históricas para os tickers USDT")
            return pd.DataFrame()

    def get_historical_klines_generator(
        self, interval: str, timestamp: str
    ) -> pd.DataFrame:
        """
        Obtém K-lines históricas usando generator (eficiente para grandes volumes)
        para os top 20 pares USDT.

        Args:
            interval: Intervalo (ex: '1h', '1d')
            timestamp: Data inicial (ex: '100 days ago UTC')

        Returns:
            DataFrame com k-lines geradas ou DataFrame vazio se falhar
        """
        df_tickers = self.get_top_20_tickers()
        symbols = df_tickers["symbol"].tolist()
        all_data = []

        if not df_tickers.empty:
            for symbol in symbols:
                data = list(
                    self.client.get_historical_klines_generator(
                        symbol=symbol, interval=interval, start_str=timestamp
                    )
                )
                if isinstance(data, list) and data:
                    for kline in data:
                        all_data.append(kline + [symbol])
                    logger.info(
                        f"K-lines históricas geradas para {symbol} via generator"
                    )
                else:
                    logger.error(f"Falha ao gerar k-lines históricas para {symbol}")

        if all_data:
            columns = [
                "Open_Time",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "Close_Time",
                "Quote_Asset_Volume",
                "Number_of_Trades",
                "Taker_Buy_Base_Asset_Volume",
                "Taker_Buy_Quote_Asset_Volume",
                "Ignore",
                "symbol",
            ]
            df = pd.DataFrame(data=all_data, columns=columns)
            df = df.drop(columns=["Ignore"])
            df["Open_Time"] = pd.to_datetime(df["Open_Time"], unit="ms").dt.strftime(
                "%d/%m/%Y %H:%M:%S"
            )
            df["Close_Time"] = pd.to_datetime(df["Close_Time"], unit="ms").dt.strftime(
                "%d/%m/%Y %H:%M:%S"
            )
            df["Number_of_Trades"] = df["Number_of_Trades"].astype(int)

            numeric_cols = [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "Quote_Asset_Volume",
                "Taker_Buy_Base_Asset_Volume",
                "Taker_Buy_Quote_Asset_Volume",
            ]

            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
            df[numeric_cols] = df[numeric_cols].round(8)
            df = df.dropna(subset=numeric_cols)

            logger.info(
                f"Geradas {len(df)} k-lines históricas para {len(symbols)} símbolos via generator"
            )
            return df
        else:
            logger.error("Falha ao gerar k-lines históricas para os tickers USDT")
            return pd.DataFrame()


