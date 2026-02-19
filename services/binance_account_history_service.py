import logging
from typing import Dict, List, Union, Optional
from env.keys import BINANCE_API_KEY, BINANCE_API_SECRET
from binance.client import Client
from binance.enums import *

logger = logging.getLogger(__name__)


class BinanceAccountService:
    """
    Serviço responsável por requisições de dados de conta na API Binance.
    
    Encapsula todas as chamadas HTTP à Binance REST API para obter:
    - Informações de saldo e balances
    - Histórico de trades executados
    - Status da conta e API
    - Ordens (abertas, fechadas, etc)
    - Histórico de dividendos
    
    Attributes:
        client: Cliente Binance já autenticado
        api_key: Chave de API Binance
        api_secret: Secret da API Binance
    """
    
    def __init__(self) -> None:
        """
        Inicializa o serviço de dados de conta.
        
        Raises:
            RuntimeError: Se não conseguir conectar à API Binance
        """
        try:
            self.api_key: str = BINANCE_API_KEY
            self.api_secret: str = BINANCE_API_SECRET
            self.client: Client = Client(self.api_key, self.api_secret, testnet=True)
            logger.info("BinanceAccountService inicializado com sucesso")
        except Exception as e:
            logger.error(f"Falha crítica ao conectar na API: {e}")
            raise RuntimeError(f"Falha crítica: Não foi possível conectar à API. Erro: {e}")

    def account_info(self) -> Union[Dict, str]:
        """
        Obtém informações completas da conta (saldo de ativos).
        
        Returns:
            Dict com dados de balances ou mensagem de erro
        """
        try:
            info = self.client.get_account()
            logger.info("Informações de conta obtidas com sucesso")
            return info
        except Exception as e:
            logger.error(f"Erro ao obter informações de conta: {e}")
            return f"An error occurred: {e}"
    
    def account_status(self) -> Union[Dict, str]:
        """
        Obtém status atual da conta.
        
        Returns:
            Dict com status da conta ou mensagem de erro
        """
        try:
            status = self.client.get_account_status()
            logger.debug("Status de conta obtido")
            return status
        except Exception as e:
            logger.error(f"Erro ao obter status de conta: {e}")
            return f"An error occurred: {e}"

    def api_trading_status(self) -> Union[Dict, str]:
        """
        Obtém status de trading da API (se está bloqueada, etc).
        
        Returns:
            Dict com status de trading ou mensagem de erro
        """
        try:
            trading_status = self.client.get_account_api_trading_status()
            logger.debug("Status de trading da API obtido")
            return trading_status
        except Exception as e:
            logger.error(f"Erro ao obter status de trading: {e}")
            return f"An error occurred: {e}"        

    def get_trades(self, symbol: str) -> Union[List[Dict], str]:
        """
        Obtém histórico de trades executados da conta para um par.
        
        Args:
            symbol: Par de moedas (ex: 'BTCUSDT')
        
        Returns:
            Lista de trades executados ou mensagem de erro
        """
        try:
            trades = self.client.get_my_trades(symbol=symbol)
            logger.debug(f"Trades obtidos para {symbol}")
            return trades
        except Exception as e:
            logger.error(f"Erro ao obter trades para {symbol}: {e}")
            return f"An error occurred: {e}"

    def get_asset_dividend_history(self, asset: Optional[str] = None) -> Union[Dict, str]:
        """
        Obtém histórico de dividendos de ativos.
        
        Args:
            asset: Ativo específico (ex: 'BNB') ou None para todos
        
        Returns:
            Dict com histórico de dividendos ou mensagem de erro
        """
        try:
            dividend_history = self.client.get_asset_dividend_history(asset=asset)
            logger.debug(f"Histórico de dividendos obtido para {asset}")
            return dividend_history
        except Exception as e:
            logger.error(f"Erro ao obter histórico de dividendos: {e}")
            return f"An error occurred: {e}"

    def get_all_orders(self, symbol: str, limit: Optional[int] = None) -> Union[List[Dict], str]:
        """
        Obtém todas as ordens (abertas, executadas, canceladas) de um par.
        
        Args:
            symbol: Par de moedas (ex: 'BTCUSDT')
            limit: Número máximo de ordens (padrão: todas)
        
        Returns:
            Lista de ordens ou mensagem de erro
        """
        try:
            orders = self.client.get_all_orders(symbol=symbol, limit=limit)
            logger.info(f"Obtidas {len(orders)} ordens para {symbol}")
            return orders
        except Exception as e:
            logger.error(f"Erro ao obter ordens para {symbol}: {e}")
            return f"An error occurred: {e}"

    def get_asset_balance(self, asset: str) -> Union[Dict, str]:
        """
        Obtém saldo de um ativo específico.
        
        Args:
            asset: Símbolo do ativo (ex: 'BTC', 'USDT')
        
        Returns:
            Dict com saldo (free e locked) ou mensagem de erro
        """
        try:
            balance = self.client.get_asset_balance(asset=asset)
            logger.debug(f"Saldo obtido para {asset}")
            return balance
        except Exception as e:
            logger.error(f"Erro ao obter saldo para {asset}: {e}")
            return f"An error occurred: {e}"