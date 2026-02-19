# ============================================================================
# CONFIGURAÇÕES GLOBAIS DO PROJETO
# ============================================================================

import logging

# Variáveis de Retry
MAX_RETRIES = 3
RETRY_DELAY = 5  # segundos

# Testnet vs Mainnet
USE_TESTNET = True

# ============================================================================
# CONFIGURAÇÃO DE LOGGING
# ============================================================================

LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%d/%m/%Y %H:%M:%S'

def setup_logging():
    """Configura o logging estruturado para toda a aplicação."""
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=[
            logging.StreamHandler(),  # Console output
            logging.FileHandler('app.log', mode='a')  # File output
        ]
    )

