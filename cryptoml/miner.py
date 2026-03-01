import ccxt
import pandas as pd
import time
from datetime import datetime

def descargar_datos(simbolo, temporalidad = '15m', años=1):
    exchange = ccxt.binance()

    desde = exchange.milliseconds() - (años * 365 * 24 * 60 * 60 * 1000)

    todas_las_velas = []

    print(f"Iniciando descarga de datos para {simbolo}...")

    while desde < exchange.milliseconds():
        try: 
            # Pedir 1000 velas a partir de la fecha 'desde'
            velas = exchange.fetch_ohlcv(simbolo, timeframe=temporalidad, since=desde, limit=1000)
            if not velas:
                print("No se recibieron más datos. Finalizando descarga.")
                break

            #Actualizar la fecha para la siguiente petición (última vela + 1 ms)

            desde = velas[-1][0] + 1
            todas_las_velas.extend(velas)
            print(f"Descargadas {len(todas_las_velas)} velas hasta {datetime.fromtimestamp(desde/1000)}")

            #pausa para no molestar a Binance
            time.sleep(0.1)

        except Exception as e:
            print(f"Error al descargar datos: {e}. Reintentando en 10 segundos...")
            time.sleep(10)

    df = pd.DataFrame(todas_las_velas, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df.to_csv(f"{simbolo.replace('/', '_')}_{temporalidad}.csv", index=False)
    print(f"Datos descargados y guardados en {simbolo.replace('/', '_')}_{temporalidad}.csv")

if __name__ == "__main__":
    descargar_datos('ETH/USDT', '15m', 1)