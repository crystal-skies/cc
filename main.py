import time 
from exchangue_handler import obtener_historial, obtener_precios
from logic_engine import Strategy

def ejecutar_bot(): 
    cerebro = Strategy()
    mis_monedas = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT'] 
    print("Iniciando el bot de criptomonedas...")

    while True:
        try: 
            # 1. Obtener precios actuales (Conexión al exchange)
            datos_actuales = obtener_precios(mis_monedas)

            for simbolo in mis_monedas:
                precio = datos_actuales[simbolo]['last']

                # 2. Historial para RSI (15 o 20 velas)
                historial = obtener_historial(simbolo, temporalidad='1m', limite=50)
                # 3. Analizar 
                resultado = cerebro.analizar(simbolo, precio, historial)

                if resultado:
                    print(f"*** {resultado} *** | Precio actual: {precio}")

            time.sleep(10)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    ejecutar_bot()