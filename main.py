import time 
import pandas as pd
from exchangue_handler import obtener_historial, obtener_precios
from logic_engine import Strategy
from risk_manager import RiskManager # Importamos tu nuevo chip

def ejecutar_bot(): 
    cerebro = Strategy()
    riesgo_control = RiskManager() # Inicializamos el gestor de riesgos
    
    mis_monedas = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT'] 
    capital_inicial = 20.0 # Esto debería venir de exchange_handler en el futuro
    
    print("🚀 Bot iniciado. Trabajando con velas de 15 minutos...")
    print("⚖️ Juez de IA y Chip de Riesgo activos.")

    while True:
        try: 
            # 1. OBTENER REFERENCIA GLOBAL (BTC)
            # Necesitamos BTC para saber si el mercado general es seguro
            velas_btc = obtener_historial('BTC/USDT', temporalidad='15m', limite=100)
            df_btc = pd.DataFrame(velas_btc, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

            # 2. Obtener precios actuales de todas las monedas
            datos_actuales = obtener_precios(mis_monedas)

            for simbolo in mis_monedas:
                precio = datos_actuales[simbolo]['last']
                
                # 3. Pedir historial de la moneda actual
                velas_moneda = obtener_historial(simbolo, temporalidad='15m', limite=250)
                df_moneda = pd.DataFrame(velas_moneda, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                
                # 4. PASO A LA IA (¿Hay oportunidad estadística?)
                # Asumo que tu Strategy devuelve un objeto con la confianza (ej: 0.74)
                resultado_ia = cerebro.analizar(simbolo, precio, velas_moneda)

                if resultado_ia:
                    confianza_ia = 0.74 # Valor de tu Random Forest
                    
                    # 5. PASO AL RISK MANAGER (¿Es seguro operar y con cuánto?)
                    veredicto = riesgo_control.get_verdict(
                        current_balance=capital_inicial,
                        df_coin=df_moneda,
                        df_btc=df_btc,
                        ia_confidence=confianza_ia,
                        symbol=simbolo
                    )

                    if veredicto['decision'] == "PROCEED":
                        print(f"\n✅ OPERACIÓN AUTORIZADA")
                        print(f"   💰 Moneda: {simbolo} | Tamaño: ${veredicto['size']}")
                        print(f"   📊 Razón: {veredicto['reason']} | ATR: {veredicto['atr']}")
                        # AQUÍ IRÍA LA ORDEN DE COMPRA REAL
                    else:
                        print(f"\n❌ SEÑAL VETADA en {simbolo}")
                        print(f"   ⚠️ Motivo: {veredicto['reason']}")

            print(".", end="", flush=True) 
            time.sleep(30)
            
        except Exception as e:
            print(f"\n❌ Error en el bucle: {e}")
            time.sleep(10)

if __name__ == "__main__":
    ejecutar_bot()