"""
Explorador de Mercado Binance - Sistema de Análise Exploratória de Dados

Extrai dados da API Binance e estrutura em DataFrames para análise.
"""
import logging
from config import setup_logging
from controllers.controllers_manager import ControllersManager

# Configurar logging global
setup_logging()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Iniciando Explorador de Mercado Binance")
    logger.info("=" * 60)
    
    try:
        # Inicializar managers com injeção de dependências
        controllers_manager = ControllersManager()
        market_data, account_history = controllers_manager.export_controllers()
        # Exemplos de uso
        data = ''
        symbol = 'BTCUSDT'
        interval = '1h'
        start_time = '2 days ago UTC'

        logger.info(f"Iniciando coleta de dados para {symbol}...")
        
        # Dados de mercado
        tickers_data = market_data.get_tickers()
        ticker24_data = market_data.get_ticker_24hr()
        orderbook_tickers_data = market_data.get_orderbook_tickers(symbol)
        klines_data = market_data.get_klines(symbol, interval)
        historical_klines_data = market_data.get_historical_klines(symbol, interval, start_time)
        average_price_data = market_data.get_avg_price(symbol)
        recent_trades_data = market_data.get_recent_trades(symbol, 1000)
        historical_trades_data = market_data.get_historical_trades(symbol)
        aggregate_trades_data = market_data.get_aggregate_trades(symbol)
        depth_data = market_data.get_depth(symbol)
        
        # Exibir amostra dos dados
        print("\n" + "="*60)
        print("AMOSTRA DOS DADOS COLETADOS (ticker 24h)")
        print("="*60)
        print(depth_data.head())
        print("="*60 + "\n")
        
        logger.info("Coleta de dados de mercado concluída com sucesso")
        logger.info("Salvando em um documento XLSX")
        tickers_data.to_excel(r'Worksheets\tickers_data.xlsx', index=False)
        ticker24_data.to_excel(r'Worksheets\ticker24_data.xlsx', index=False)
        orderbook_tickers_data.to_excel(r'Worksheets\orderbook_tickers_data.xlsx', index=False)
        klines_data.to_excel(r'Worksheets\klines_data.xlsx', index=False)
        historical_klines_data.to_excel(r'Worksheets\historical_klines_data.xlsx', index=False)
        average_price_data.to_excel(r'Worksheets\average_price_data.xlsx', index=False)
        recent_trades_data.to_excel(r'Worksheets\recent_trades_data.xlsx', index=False)
        historical_trades_data.to_excel(r'Worksheets\historical_trades_data.xlsx', index=False)
        aggregate_trades_data.to_excel(r'Worksheets\aggregate_trades_data.xlsx', index=False)
        depth_data.to_excel(r'Worksheets\depth_data.xlsx', index=False)

    except Exception as e:
        logger.error(f"Erro durante execução: {e}", exc_info=True)
        raise


