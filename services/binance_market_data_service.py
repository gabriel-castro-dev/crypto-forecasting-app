import logging
from typing import Dict, List, Optional, Union, Generator
from env.keys import BINANCE_API_KEY, BINANCE_API_SECRET
from binance.client import Client
from binance.enums import *

logger = logging.getLogger(__name__)


class BinanceMarketService:
    """
    Serviço responsável por requisições de dados de mercado na API Binance.
    
    Encapsula todas as chamadas HTTP à Binance REST API para obter:
    - Informações de tickers e preços
    - Dados de ordem book
    - K-lines (velas) históricas
    - Trades e transações de mercado
    
    Attributes:
        client: Cliente Binance já autenticado
        api_key: Chave de API Binance
        api_secret: Secret da API Binance
    """
    
    def __init__(self) -> None:
        """
        Inicializa o serviço de dados de mercado.
        
        Raises:
            RuntimeError: Se não conseguir conectar à API Binance
        """
        try:
            self.api_key: str = BINANCE_API_KEY
            self.api_secret: str = BINANCE_API_SECRET
            self.client: Client = Client(self.api_key, self.api_secret, testnet=True)
            logger.info("BinanceMarketService inicializado com sucesso")
        except Exception as e:
            logger.error(f"Falha crítica ao conectar na API: {e}")
            raise RuntimeError(f"Falha crítica: Não foi possível conectar à API. Erro: {e}")

    def ping(self) -> Union[Dict, str]:
        """
        Verifica conectividade com a API Binance.
        
        Returns:
            Dict vazio se conexão OK, ou mensagem de erro
        """
        try:
            result = self.client.ping()
            logger.debug("Ping bem-sucedido na API Binance")
            return result
        except Exception as e:
            logger.error(f"Erro ao fazer ping na API: {e}")
            return f"Error pinging Binance API: {e}"

    def server_time(self) -> Union[Dict, str]:
        """
        Obtém o horário atual do servidor Binance.
        
        Returns:
            Dict com timestamp ou mensagem de erro
        """
        try:
            result = self.client.get_server_time()
            return result
        except Exception as e:
            logger.error(f"Erro ao obter tempo do servidor: {e}")
            return f"Error getting server time: {e}"

    def system_status(self) -> Union[Dict, str]:
        """
        Obtém status do sistema Binance.
        
        Returns:
            Dict com status ou mensagem de erro
        """
        try:
            result = self.client.get_system_status()
            return result
        except Exception as e:
            logger.error(f"Erro ao obter status do sistema: {e}")
            return f"Error getting system status: {e}"

    def get_tickers(self) -> Union[List[Dict], str]:
        """
        Obtém lista de todos os tickers de mercado.
        
        Returns:
            Lista de dicts com informações de tickers ou mensagem de erro
        """
        try:
            tickers = self.client.get_all_tickers()
            logger.info(f"Obtidas informações de {len(tickers)} tickers")
            return tickers
        except Exception as e:
            logger.error(f"Erro ao obter tickers: {e}")
            return f"Error getting tickers: {e}"

    def get_ticker_24hr(self, symbol: str) -> Union[Dict, str]:
        """
        Obtém informações de 24h de um par específico.
        
        Args:
            symbol: Par de moedas (ex: 'BTCUSDT')
        
        Returns:
            Dict com dados 24h ou mensagem de erro
        """
        try:
            ticker_24hr = self.client.get_ticker(symbol=symbol)
            logger.debug(f"Ticker 24h obtido para {symbol}")
            return ticker_24hr
        except Exception as e:
            logger.error(f"Erro ao obter ticker 24h para {symbol}: {e}")
            return f"Error getting 24hr ticker for {symbol}: {e}"

    def get_orderbook_tickers(self, symbol: str) -> Union[Dict, str]:
        """
        Obtém informações de order book de um par.
        
        Args:
            symbol: Par de moedas (ex: 'BTCUSDT')
        
        Returns:
            Dict com dados de order book ou mensagem de erro
        """
        try:
            orderbook_tickers = self.client.get_orderbook_tickers(symbol=symbol)
            logger.debug(f"Order book obtido para {symbol}")
            return orderbook_tickers
        except Exception as e:
            logger.error(f"Erro ao obter order book para {symbol}: {e}")
            return f"Error getting orderbook tickers for {symbol}: {e}"

    def get_klines(self, symbol: str, interval: str) -> Union[List[List], str]:
        """
        Obtém K-lines (velas) em tempo real de um par.
        
        Args:
            symbol: Par de moedas (ex: 'BTCUSDT')
            interval: Intervalo de tempo (ex: '1m', '1h', '1d')
        
        Returns:
            Lista de K-lines ou mensagem de erro
        """
        try:
            klines = self.client.get_klines(symbol=symbol, interval=interval)
            logger.debug(f"K-lines obtidas para {symbol} no intervalo {interval}")
            return klines
        except Exception as e:
            logger.error(f"Erro ao obter k-lines para {symbol}: {e}")
            return f"Error getting klines for {symbol}: {e}"

    def get_historical_klines(self, symbol: str, interval: str, start_str: str, 
                             end_str: Optional[str] = None, limit: int = 1000) -> Union[List[List], str]:
        """
        Obtém K-lines históricas de um período específico.
        
        Args:
            symbol: Par de moedas (ex: 'BTCUSDT')
            interval: Intervalo de tempo (ex: '1h', '1d')
            start_str: Data inicial (ex: '10 days ago UTC' ou timestamp)
            end_str: Data final (opcional)
            limit: Número máximo de resultados
        
        Returns:
            Lista de K-lines ou mensagem de erro
        """
        try:
            klines = self.client.get_historical_klines(symbol, interval, start_str, end_str, limit=limit)
            logger.info(f"Obtidas {len(klines)} k-lines históricas para {symbol}")
            return klines
        except Exception as e:
            logger.error(f"Erro ao obter k-lines históricas para {symbol}: {e}")
            return f"Error getting historical klines for {symbol}: {e}"

    def get_historical_klines_generator(self, symbol: str, interval: str, 
                                       timestamp: str) -> Generator[Union[Dict, str], None, None]:
        """
        Obtém K-lines históricas como generator (eficiente para grandes volumes).
        
        Args:
            symbol: Par de moedas (ex: 'BTCUSDT')
            interval: Intervalo de tempo (ex: '1h', '1d')
            timestamp: Data inicial (ex: '100 days ago UTC')
        
        Yields:
            Dict com cada k-line ou mensagem de erro
        """
        try:
            columns = ['Open_Time', 'Open', 'High', 'Low', 'Close', 'Volume',
                      'Close_Time', 'Quote_Asset_Volume', 'Number_of_Trades',
                      'Taker_Buy_Base_Asset_Volume', 'Taker_Buy_Quote_Asset_Volume', 'Ignore']
            
            for kline in self.client.get_historical_klines_generator(symbol, interval, timestamp):
                historical_klines_dict = dict(zip(columns, kline))
                yield historical_klines_dict
            logger.info(f"Generator de k-lines históricas concluído para {symbol}")
        except Exception as e:
            logger.error(f"Erro ao gerar k-lines históricas para {symbol}: {e}")
            yield f"Error getting historical klines generator for {symbol}: {e}"

    def get_avg_price(self, symbol: str) -> Union[Dict, str]:
        """
        Obtém preço médio de um par.
        
        Args:
            symbol: Par de moedas (ex: 'BTCUSDT')
        
        Returns:
            Dict com preço médio ou mensagem de erro
        """
        try:
            avg_price = self.client.get_avg_price(symbol=symbol)
            logger.debug(f"Preço médio obtido para {symbol}")
            return avg_price
        except Exception as e:
            logger.error(f"Erro ao obter preço médio para {symbol}: {e}")
            return f"Error getting average price for {symbol}: {e}"

    def get_recent_trades(self, symbol: str, limit: None) -> Union[List[Dict], str]:
        """
        Obtém trades recentes de um par.
        
        Args:
            symbol: Par de moedas (ex: 'BTCUSDT')
        
        Returns:
            Lista de trades recentes ou mensagem de erro
        """
        try:
            recent_trades = self.client.get_recent_trades(symbol=symbol, limit = limit)
            logger.debug(f"Trades recentes obtidos para {symbol}")
            return recent_trades
        except Exception as e:
            logger.error(f"Erro ao obter trades recentes para {symbol}: {e}")
            return f"Error getting recent trades for {symbol}: {e}"

    def get_historical_trades(self, symbol: str) -> Union[List[Dict], str]:
        """
        Obtém histórico de trades de um par.
        
        Args:
            symbol: Par de moedas (ex: 'BTCUSDT')
        
        Returns:
            Lista de trades históricos ou mensagem de erro
        """
        try:
            historical_trades = self.client.get_historical_trades(symbol=symbol)
            logger.debug(f"Trades históricos obtidos para {symbol}")
            return historical_trades
        except Exception as e:
            logger.error(f"Erro ao obter trades históricos para {symbol}: {e}")
            return f"Error getting historical trades for {symbol}: {e}"

    def get_aggregate_trades(self, symbol: str) -> Union[List[Dict], str]:
        """
        Obtém agregação de trades de um par.
        
        Args:
            symbol: Par de moedas (ex: 'BTCUSDT')
        
        Returns:
            Lista de trades agregados ou mensagem de erro
        """
        try:
            aggregate_trades = self.client.get_aggregate_trades(symbol=symbol)
            logger.debug(f"Trades agregados obtidos para {symbol}")
            return aggregate_trades
        except Exception as e:
            logger.error(f"Erro ao obter trades agregados para {symbol}: {e}")
            return f"Error getting aggregate trades for {symbol}: {e}"

    def get_depth(self, symbol: str) -> Union[Dict, str]:
        """
        Obtém profundidade de mercado (order book depth) de um par.
        
        Args:
            symbol: Par de moedas (ex: 'BTCUSDT')
        
        Returns:
            Dict com dados de profundidade ou mensagem de erro
        """
        try:
            depth = self.client.get_order_book(symbol=symbol)
            logger.debug(f"Profundidade de mercado obtida para {symbol}")
            return depth
        except Exception as e:
            logger.error(f"Erro ao obter profundidade de mercado para {symbol}: {e}")
            return f"Error getting order book for {symbol}: {e}"

    