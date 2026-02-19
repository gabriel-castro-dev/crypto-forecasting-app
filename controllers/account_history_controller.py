import logging
from typing import Optional, Tuple, Union
import pandas as pd
import time
from config import MAX_RETRIES, RETRY_DELAY
from services.binance_account_history_service import BinanceAccountService
from controllers.market_data_controller import MarketDataController

logger = logging.getLogger(__name__)


class AccountHistoryController:
    """
    Controlador responsável por transformação e tratamento de dados de conta.
    
    Converte respostas brutas da API Binance em DataFrames estruturados:
    - Informações de saldo e balances
    - Histórico de trades executados
    - Ordens e status de trading
    - Histórico de dividendos
    
    Attributes:
        account_history_service: Instância de BinanceAccountService (injetada)
        market_data: Instância de MarketDataController para validação de conectividade
    """
    
    def __init__(self, account_history_service: BinanceAccountService, 
                 market_data: MarketDataController) -> None:
        """
        Inicializa o controller com dependências injetadas.
        
        Args:
            account_history_service: Serviço de dados de conta (DI)
            market_data: Controller de dados de mercado para health checks
        
        Raises:
            Exception: Se falhar na inicialização
        """
        try:
            self.account_history_service: BinanceAccountService = account_history_service
            self.market_data: MarketDataController = market_data
            logger.info("AccountHistoryController inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar AccountHistoryController: {e}")
            raise
    
    def account_info(self) -> Union[pd.DataFrame, str]:
        """
        Obtém informações de saldo dos ativos da conta.
        
        Returns:
            DataFrame com ativos com saldo > 0 ou mensagem de erro
        """
        for attempt in range(MAX_RETRIES):
            data = self.account_history_service.account_info()
            if isinstance(data, dict):
                df = pd.DataFrame(data['balances'])
                df[['free', 'locked']] = df[['free', 'locked']].astype(float).round(4)
                df = df[(df['free'] > 0) | (df['locked'] > 0)].reset_index(drop=True)
                df['asset'] = df['asset'].astype(str)
                logger.info(f"Obtidas informações de compte com {len(df)} ativos com saldo")
                return df
            elif not data or isinstance(data, str):
                if ("APIError(code=-2015)" in data):
                    logger.error("Erro de permissão ao obter informações de conta")
                    raise PermissionError(f"Failed to retrieve account info, user doesn't have permission to do this request.")   
                logger.warning(f"[Tentativa {attempt + 1}/{MAX_RETRIES}] {data}")
                status = self.market_data.ping()
                if status != "Binance API is reachable.":
                    logger.warning(f"Problema de conectividade. Aguardando {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY) 

        logger.error("Falha ao obter informações de conta")
        return "failed to get account info, error:"

    def account_status(self) -> str:
        """
        Obtém estado atual da conta (Normal, Locked, etc).
        
        Returns:
            String com status ou mensagem de erro/orientação
        """
        url = 'https://www.binance.com/pt-BR/my/dashboard'
        for attempt in range(MAX_RETRIES):
            data = self.account_history_service.account_status()
            if isinstance(data, dict):
                if 'Normal' in data.values():
                    logger.info("Status de conta: Normal")
                    return 'Account is ok!'
                if data != 'Normal':
                    msg = f'Please check account status on binance, possible pendencies.{url}'
                    logger.warning(f"Conta com status pendente: {msg}")
                    return msg
            elif not data or isinstance(data, str):
                if ("APIError(code=-2015)" in data):
                    logger.error("Erro de permissão ao obter status de conta")
                    raise PermissionError(f"Failed to retrieve account status, user doesn't have permission to do this request.")   
                logger.warning(f"[Tentativa {attempt + 1}/{MAX_RETRIES}] {data}")
                status = self.market_data.ping()
                if status != "Binance API is reachable.":
                    logger.warning(f"Problema de conectividade. Aguardando {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY) 

        logger.error("Falha ao obter status de conta")
        return "failed to get account status"

    def api_trading_status(self) -> Union[Tuple[str, str, str], str]:
        """
        Obtém status de trading da API (se está bloqueada para trading).
        
        Returns:
            Tupla (UFR, IFER, GCR) se desbloqueada, ou mensagem de erro
        """
        for attempt in range(MAX_RETRIES):
            data = self.account_history_service.api_trading_status()
            if isinstance(data, dict):
                if data['data']['isLocked'] == False:
                    UFR = data['data']['triggerCondition']['UFR']
                    IFER = data['data']['triggerCondition']['IFER']
                    GCR = data['data']['triggerCondition']['GCR']
                    updateTime = data['data']['updateTime']
                    msg = f"Trading status ok for now, please be careful if trigger conditions: Unfilled Order Ratio = {UFR}, Immediate Fill or Kill Ratio {IFER}, GTC Cancel Ratio{GCR}, conditions will be updated in: {updateTime}"
                    logger.info("Status de trading desbloqueado")
                    logger.info(msg)
                    return UFR, IFER, GCR
                elif data['data']['isLocked'] == True:
                    recoverTime = data['data']['plannedRecoverTime']
                    msg = f"Account is locked for trading, will be recovered in: {recoverTime}"
                    logger.warning(msg)
                    return msg
            elif not data or isinstance(data, str):
                if ("APIError(code=-2015)" in data):
                    logger.error("Erro de permissão ao obter status de trading")
                    return(f"Failed to retrieve account status, user doesn't have permission to do this request.")   
                logger.warning(f"[Tentativa {attempt + 1}/{MAX_RETRIES}] {data}")
                status = self.market_data.ping()
                if status != "Binance API is reachable.":
                    logger.warning(f"Problema de conectividade. Aguardando {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY) 

        logger.error("Falha ao obter status de trading")
        return "failed to get trading status"
    
    def get_trades(self, symbol: str) -> pd.DataFrame:
        """
        Obtém histórico de trades executados da conta para um par.
        
        Args:
            symbol: Par de moedas (ex: 'BTCUSDT')
        
        Returns:
            DataFrame com trades executados ou DataFrame vazio se falhar
        """
        for attempt in range(MAX_RETRIES):
            data = self.account_history_service.get_trades(symbol=symbol)
            if isinstance(data, list):
                df = pd.DataFrame(data)
                df[['symbol', 'commissionAsset']] = df[['symbol', 'commissionAsset']].astype(str)
                df[['id', 'orderId', 'orderListId']] = df[['id', 'orderId', 'orderListId']].astype(int)
                df = df.drop_duplicates(subset=['id']).reset_index(drop=True).set_index('id')
                df[['price', 'qty', 'quoteQty', 'commission']] = df[['price', 'qty', 'quoteQty', 'commission']].astype(float)
                df['price'] = df['price'].round(2).dropna() 
                df['time'] = pd.to_datetime(df['time'], unit='ms').dt.strftime('%d/%m/%Y %H:%M:%S')
                df[['isBuyer', 'isMaker', 'isBestMatch']] = df[['isBuyer', 'isMaker', 'isBestMatch']].astype(bool, errors='ignore')
                logger.info(f"Obtidos {len(df)} trades para {symbol}")
                return df
            elif not data or isinstance(data, str):
                if ("APIError(code=-2015)" in data):
                    logger.error(f"Erro de permissão para {symbol}")
                    raise PermissionError(f"Failed to get trades for {symbol}, user doesn't have permission to do this request.")
                if ("APIError(code=-1100)" in data or "APIError(code=-1121)" in data):
                    logger.error(f"Símbolo inválido: {symbol}")
                    raise KeyError(f"Failed to get trades for {symbol}, invalid symbol provided.")   
                logger.warning(f"[Tentativa {attempt + 1}/{MAX_RETRIES}] {data}")
                status = self.market_data.ping()
                if status != "Binance API is reachable.":
                    logger.warning(f"Problema de conectividade. Aguardando {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY) 

        logger.error(f"Falha ao obter trades para {symbol}")
        return pd.DataFrame()
    
    def get_asset_dividend_history(self, symbol: Optional[str] = None) -> pd.DataFrame:
        """
        Obtém histórico de dividendos de ativos da conta.
        
        Args:
            symbol: Ativo específico (ex: 'BNB') ou None para todos
        
        Returns:
            DataFrame com histórico de dividendos ou DataFrame vazio se não houver
        """
        for attempt in range(MAX_RETRIES):
            data = self.account_history_service.get_asset_dividend_history(symbol=symbol)
            if isinstance(data, dict) and data.get('total', 0) != 0:
                logger.info(f"Histórico de dividendos encontrado: {data['total']} registros")
                df = pd.DataFrame(data['rows'])
                df[['id', 'tranId']] = df[['id', 'tranId']].astype(int)
                df = df.drop_duplicates(subset=['id']).reset_index(drop=True).set_index('id')
                df['amount'] = df['amount'].astype(float).round(8)
                df['divTime'] = pd.to_datetime(df['divTime'], unit='ms').dt.strftime('%d/%m/%Y %H:%M:%S')
                df[['asset', 'enInfo']] = df[['asset', 'enInfo']].astype(str)
                return df
            elif isinstance(data, dict) and data.get('total', 0) == 0:
                logger.info(f"Nenhum histórico de dividendos encontrado para {symbol}")
                return pd.DataFrame()
            elif not data or isinstance(data, str):
                if ("APIError(code=-2015)" in data):
                    logger.error("Erro de permissão ao obter histórico de dividendos")
                    raise PermissionError(f"Failed to get asset dividend history, user doesn't have permission to do this request.")
                if ("APIError(code=-1100)" in data or "APIError(code=-1121)" in data):
                    logger.error("Parâmetro inválido no histórico de dividendos")
                    raise KeyError(f"Failed to get asset dividend history, invalid parameters provided.")   
                logger.warning(f"[Tentativa {attempt + 1}/{MAX_RETRIES}] {data}")
                status = self.market_data.ping()
                if status != "Binance API is reachable.":
                    logger.warning(f"Problema de conectividade. Aguardando {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY) 

        logger.error("Falha ao obter histórico de dividendos")
        return pd.DataFrame()
    
    def get_all_orders(self, symbol: str, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Obtém todas as ordens (abertas, executadas, canceladas) de um par.
        
        Args:
            symbol: Par de moedas (ex: 'BTCUSDT')
            limit: Limite de ordens a retornar (None = todas)
        
        Returns:
            DataFrame com ordens ou DataFrame vazio se falhar/vazia
        """
        for attempt in range(MAX_RETRIES):
            data = self.account_history_service.get_all_orders(symbol=symbol, limit=limit)
            if isinstance(data, list) and len(data) > 0:
                if not data:
                    logger.info(f"Nenhum histórico de ordens para {symbol}")
                    return pd.DataFrame()
                
                df = pd.DataFrame(data)
                df = df[["symbol", "orderId", "orderListId", "clientOrderId", "price",
                         "origQty", "executedQty", "cummulativeQuoteQty", "status", "timeInForce",
                         "type", "side", "stopPrice", "icebergQty", "time", "updateTime"]]
                df[['orderId', 'orderListId']] = df[['orderId', 'orderListId']].astype(int)
                df = df.drop_duplicates(subset=['orderId']).reset_index(drop=True).set_index('orderId')
                df[["symbol", "clientOrderId", "status", "timeInForce", "type", "side"]] = \
                    df[["symbol", "clientOrderId", "status", "timeInForce", "type", "side"]].astype(str).fillna(
                        "Field not avaliable for this type of operation")
                df[['price', 'origQty', 'executedQty', 'cummulativeQuoteQty',
                    'stopPrice', 'icebergQty']] = df[['price', 'origQty', 'executedQty',
                                                      'cummulativeQuoteQty', 'stopPrice', 'icebergQty']].astype(float, errors='ignore').fillna(0.00)
                df['price'] = df['price'].round(2) 
                for col in ['time', 'updateTime']:
                    df[col] = pd.to_datetime(df[col], unit="ms").dt.strftime('%d/%m/%Y %H:%M:%S')
                logger.info(f"Obtidas {len(df)} ordens para {symbol}")
                return df         
            elif not data or isinstance(data, str):      
                if ("APIError(code=-2015)" in data):
                    logger.error("Erro de permissão ao obter ordens")
                    raise PermissionError(f"Failed to get all orders, user doesn't have permission to do this request.") 
                if ("APIError(code=-1100)" in data or "APIError(code=-1121)" in data):
                    logger.error("Parâmetro inválido em ordens")
                    raise KeyError(f"Failed to get asset dividend history, invalid parameters provided.")                   
                logger.warning(f"[Tentativa {attempt + 1}/{MAX_RETRIES}] {data}")
                status = self.market_data.ping()
                if status != "Binance API is reachable.":
                    logger.warning(f"Problema de conectividade. Aguardando {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY)                                      

        logger.error(f"Falha ao obter ordens para {symbol}")
        return pd.DataFrame()    
    
    def get_asset_balance(self, symbol: str) -> pd.DataFrame:
        """
        Obtém saldo de um ativo específico.
        
        Args:
            symbol: Símbolo do ativo (ex: 'BTC', 'USDT')
        
        Returns:
            DataFrame com saldo (free e locked) ou DataFrame vazio se falhar
        """
        for attempt in range(MAX_RETRIES):
            data = self.account_history_service.get_asset_balance(symbol=symbol)
            if isinstance(data, dict):
                df = pd.DataFrame([data])
                df['asset'] = df['asset'].astype(str)
                df[['free', 'locked']] = df[['free', 'locked']].astype(float, errors='ignore').round(6)
                logger.info(f"Saldo obtido para {symbol}")
                return df
            elif not data or isinstance(data, str):
                if ("APIError(code=-2015)" in data):
                    logger.error(f"Erro de permissão para {symbol}")
                    raise PermissionError(f"Failed to get asset dividend history, user doesn't have permission to do this request.")
                if ("APIError(code=-1100)" in data or "APIError(code=-1121)" in data):
                    logger.error(f"Símbolo inválido: {symbol}")
                    raise KeyError(f"Failed to get asset dividend history, invalid parameters provided.")   
                logger.warning(f"[Tentativa {attempt + 1}/{MAX_RETRIES}] {data}")
                status = self.market_data.ping()
                if status != "Binance API is reachable.":
                    logger.warning(f"Problema de conectividade. Aguardando {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY) 

        logger.error(f"Falha ao obter saldo para {symbol}")
        return pd.DataFrame()
    