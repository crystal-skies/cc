import pandas as pd
import numpy as np
import joblib
import pandas_ta as ta
from logic_engine import Strategy 

def ejecutar_backtesting(archivo_datos):
    print(f"--- Iniciando Backtesting Real: {archivo_datos} ---")
    
    # 1. Cargar Datos
    df = pd.read_csv(archivo_datos)
    
    # 2. Inicializar tu Motor de Lógica
    bot = Strategy()
    
    # 3. Variables de Seguimiento
    capital = 20.0
    posicion_abierta = False
    precio_entrada = 0
    tipo_operacion = None
    trades = []
    
    # Parámetros (Ajustados a tu processor)
    TP = 0.008  
    SL = 0.015  
    COMISION = 0.0025 
    HORIZONTE = 32 

    # 4. Bucle de Simulación
    # Empezamos en 800 para que las EMAs tengan datos suficientes
    for i in range(800, len(df)):
        # Ventana de datos actual
        ventana = df.iloc[i-800:i+1].copy()
        
        # Usamos 'timestamp' porque así se llama en tu CSV
        ultimo_registro = ventana.iloc[-1]
        precio_actual = ultimo_registro['close']
        ts_actual = ultimo_registro['timestamp'] 

        if not posicion_abierta:
            # IMPORTANTE: Pasamos los valores para que Strategy cree su DataFrame
            # Tu Strategy espera columnas: ['ts', 'open', 'high', 'low', 'close', 'volume']
            # Así que enviamos los datos en ese orden exacto.
            datos_para_chips = ventana[['timestamp', 'open', 'high', 'low', 'close', 'volume']].values
            
            resultado = bot.analizar("BTC/USDT", precio_actual, datos_para_chips)
            
            if resultado:
                posicion_abierta = True
                precio_entrada = precio_actual
                tipo_operacion = 'COMPRA' if '🟢' in resultado else 'VENTA'
                velas_transcurridas = 0
                print(f"[{ts_actual}] ENTRADA a {precio_actual} ({tipo_operacion})")

        else:
            velas_transcurridas += 1
            # Calcular cambio de precio
            if tipo_operacion == 'COMPRA':
                cambio = (precio_actual - precio_entrada) / precio_entrada
            else:
                cambio = (precio_entrada - precio_actual) / precio_entrada

            # Condiciones de salida
            if cambio >= (TP + COMISION):
                resultado_trade = "GANANCIA"
                capital *= (1 + TP) # Ganancia neta
                posicion_abierta = False
            elif cambio <= -(SL - COMISION):
                resultado_trade = "PÉRDIDA"
                capital *= (1 - SL) # Pérdida neta
                posicion_abierta = False
            elif velas_transcurridas >= HORIZONTE:
                resultado_trade = "TIEMPO"
                ganancia_final = cambio - COMISION
                capital *= (1 + ganancia_final)
                posicion_abierta = False
            # timepo es cuando el trade se cierra por superar el horizonte de 32 velas sin alcanzar ni TP ni SL

            if not posicion_abierta:
                trades.append(1 if resultado_trade == "GANANCIA" else 0)
                print(f"[{ts_actual}] SALIDA: {resultado_trade} | Capital: ${capital:.2f}")

    # 5. RESULTADOS
    if len(trades) > 0:
        win_rate_real = (sum(trades) / len(trades)) * 100
        print("\n" + "="*30)
        print(f"Trades: {len(trades)} | Win Rate: {win_rate_real:.2f}%")
        print(f"Capital Final: ${capital:.2f}")
        print("="*30)
    else:
        print("No se ejecutó ningún trade. Revisa los umbrales del Juez.")

if __name__ == "__main__":
    ejecutar_backtesting('cryptoml/BTC_USDT_15m.csv')