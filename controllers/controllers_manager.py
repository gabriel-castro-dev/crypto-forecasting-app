import logging
from typing import Tuple
from controllers.account_history_controller import AccountHistoryController
from controllers.market_data_controller import MarketDataController
from services.services_manager import ServicesManager

logger = logging.getLogger(__name__)


class ControllersManager:
    """
    Factory de controladores que centraliza criação e injeção de dependências.
    
    Implements Factory Pattern e Dependency Injection para:
    - Criar e configurar todos os controladores de uma vez
    - Injetar serviços nos controladores
    - Centralizar lógica de inicialização
    
    Attributes:
        services_manager: Manager que fornece os serviços
        market_data_controller: Instância de controlador de dados de mercado
        account_history_controller: Instância de controlador de histórico de conta
    """
    
    def __init__(self) -> None:
        """
        Inicializa o manager criando instâncias de todos os controladores.
        
        Raises:
            Exception: Se algum controlador falhar na inicialização
        """
        try:
            # Criar serviços
            services_manager = ServicesManager()
            market_data_service, account_history_service = services_manager.export_services()
            
            # Injetar dependências nos controladores
            self.market_data_controller: MarketDataController = MarketDataController(market_data_service)
            self.account_history_controller: AccountHistoryController = AccountHistoryController(
                account_history_service, 
                self.market_data_controller
            )
            logger.info("ControllersManager inicializado com injeção de dependências")
        except Exception as e:
            logger.error(f"Erro ao inicializar ControllersManager: {e}")
            raise

    def export_controllers(self) -> Tuple[MarketDataController, AccountHistoryController]:
        """
        Retorna tupla com instâncias dos controladores.
        
        Returns:
            Tupla (MarketDataController, AccountHistoryController)
        """
        logger.debug("Exportando controladores from ControllersManager")
        return self.market_data_controller, self.account_history_controller
    