# Etapa de conexión 
import ccxt

exchange = ccxt.binance()  

def obtener_precios(lista_monedas):
    """
    Esta función recibe una lista de monedas y 
    devuelve la información completa de sus precios.
    """
    try:
        # 2. Pedir Tickers de la lista recibida
        tickers = exchange.fetch_tickers(lista_monedas)
        return tickers
    except Exception as e:
        print(f"Error al conectar con el exchange: {e}")
        return {}
    

def obtener_historial(simbolo, temporalidad='1h', limite=100):
    """ Trae las últimas 'X' velas (OHLCV) de una moneda. 
        el OHLCV es:
        Open: precio al que empezó la hora
        High: precio más alto de la hora
        Low: precio más bajo de la hora
        Close: precio final de la hora
        Volume: volumen de transacciones en esa hora.

        La vela es la forma visual. Si el precio subió, la 
        vela es verde (o blanca), si bajó, es roja (o negra).
    """
    try: 
        historial = exchange.fetch_ohlcv(simbolo,timeframe=temporalidad, limit=limite)
        return historial
    except Exception as e:
        print(f"Error al obtener historial: {e}")
        return []
    
    

