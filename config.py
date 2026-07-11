import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MAX_RETRIES = 3
    RETRY_DELAY = 5  
    SUPABASE_URL: str
    SUPABASE_KEY: str
    BINANCE_API_KEY: str
    BINANCE_API_SECRET: str
    USE_TESTNET = True

    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%d/%m/%Y %H:%M:%S'

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


def setup_logging():  
        
    logging.basicConfig(
        level=settings.LOG_LEVEL,         
        format=settings.LOG_FORMAT,       
        datefmt=settings.LOG_DATE_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log', mode='a')
            ]
        )

settings = Settings()



