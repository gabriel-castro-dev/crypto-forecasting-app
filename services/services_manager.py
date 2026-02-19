import logging
from typing import Tuple
from services.binance_account_history_service import BinanceAccountService
from services.binance_market_data_service import BinanceMarketService

logger = logging.getLogger(__name__)


class ServicesManager:
    """
    Factory de serviços que centraliza a criação e gerenciamento de instâncias.
    
    Implements Factory Pattern para:
    - Criar e configurar todos os serviços de uma vez
    - Facilitar injeção de dependências
    - Centralizar lógica de inicialização
    
    Attributes:
        market_data_service: Instância de serviço de dados de mercado
        account_history_service: Instância de serviço de dados de conta
    """
    
    def __init__(self) -> None:
        """
        Inicializa o manager criando instâncias de todos os serviços.
        
        Raises:
            RuntimeError: Se algum serviço falhar na inicialização
        """
        try:
            self.market_data_service: BinanceMarketService = BinanceMarketService()
            self.account_history_service: BinanceAccountService = BinanceAccountService()
            logger.info("ServicesManager inicializado com todos os serviços")
        except Exception as e:
            logger.error(f"Erro ao inicializar ServicesManager: {e}")
            raise

    def export_services(self) -> Tuple[BinanceMarketService, BinanceAccountService]:
        """
        Retorna tupla com instâncias dos serviços.
        
        Returns:
            Tupla (BinanceMarketService, BinanceAccountService)
        """
        logger.debug("Exportando serviços from ServicesManager")
        return self.market_data_service, self.account_history_service