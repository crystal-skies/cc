import pandas as pd
import pandas_ta as ta

def procesar_y_etiquetar(archivo_entrada):
    df = pd.read_csv(archivo_entrada)
    print(f"Generando materia prima para el Chip de ML...")

    # --- 1. FEATURES (Los ojos del Juez) ---
    df['RSI'] = ta.rsi(df['close'], length=14)
    df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    df['Volumen_Relativo'] = df['volume'] / df['volume'].rolling(window=20).mean()
    
    sma200 = ta.sma(df['close'], length=200)
    df['distancia_sma200'] = (df['close'] - sma200) / sma200
    
    sma50 = ta.sma(df['close'], length=50)
    df['tendencia_superior'] = sma50.diff(periods=5) 
    
    df['momentum'] = ta.roc(df['close'], length=10)

    #EMA200
    df['emma200'] = ta.ema(df['close'], length=200)
    df['distancia_emma200'] = (df['close'] - df['emma200']) / df['emma200']

    #EMA800
    df['emma800'] = ta.ema(df['close'], length=800)
    df['tendencia_macro'] = (df['close'] > df['emma800']).astype(int) # 1 si es alcista macro, 0 si es bajista

    #PRICE ACTION FEATURES
    rango_total = df['high'] - df['low']
    cuerpo = (df['close'] - df['open']).abs()
    df['calidad_cuerpo'] = cuerpo / (rango_total + 1e-9) # Evitar división por cero

    # Mechas
    df['mecha_superior'] = (df['high'] - df[['close', 'open']].max(axis=1)) / (rango_total + 1e-9)
    df['mecha_inferior'] = (df[['close', 'open']].min(axis=1) - df['low']) / (rango_total + 1e-9)

    #Volatilidad relativa
    df['volatilidad_rel'] = df['ATR'] / df['close']
    
    # RSI de "Cámara Lenta" (Para que el Juez vea la tendencia del RSI)
    df['RSI_lento'] = ta.rsi(df['close'], length=50)


    # --- 2. LABELING CONSERVADOR (La meta del Juez) ---
    df['target'] = 0 
    
    tp_deseado = 0.008  # 0.8% ganancia limpia
    sl_deseado = 0.015  # 1.5% pérdida máxima (margen de seguridad)
    friccion = 0.0025   # Comisiones de Binance + Slippage
    
    tp_real = tp_deseado + friccion # El precio debe subir 1.05%
    sl_real = sl_deseado - friccion # El precio debe bajar 1.25% para perder
    
    horizonte = 32 # El éxito debe ocurrir en las siguientes 12 horas

    for i in range(len(df) - horizonte):
        rsi_actual = df.loc[i, 'RSI']
        precio_entrada = df.loc[i, 'close']

        # Disparador del Chip Técnico: RSI en zonas de interés
        if rsi_actual < 35: # Posible COMPRA
            for j in range(1, horizonte + 1):
                cambio = (df.loc[i + j, 'close'] - precio_entrada) / precio_entrada
                if cambio >= tp_real:
                    df.loc[i, 'target'] = 1  # ÉXITO
                    break
                if cambio <= -sl_real:
                    df.loc[i, 'target'] = 0  # FRACASO
                    break
                    
        elif rsi_actual > 65: # Posible VENTA
            for j in range(1, horizonte + 1):
                cambio_short = (precio_entrada - df.loc[i + j, 'close']) / precio_entrada
                if cambio_short >= tp_real:
                    df.loc[i, 'target'] = 1  # ÉXITO
                    break
                if cambio_short <= -sl_real:
                    df.loc[i, 'target'] = 0  # FRACASO
                    break

    df.dropna(inplace=True)
    nombre_salida = "dataset_para_el_juezETH.csv"
    df.to_csv(nombre_salida, index=False)

    # Estadísticas para saber qué tan difícil la tiene el Juez
    num_exitos = df['target'].sum()
    total_señales = len(df[(df['RSI'] < 35) | (df['RSI'] > 65)])
    
    print(f"--- REPORTE DE DATOS ---")
    print(f"Tasa de éxito natural (sin IA): {(num_exitos/total_señales)*100:.2f}%")
    print(f"¡Dataset listo! El Juez tiene {num_exitos} ejemplos de éxito para estudiar.")
    
    return nombre_salida     

if __name__ == "__main__":
    procesar_y_etiquetar('ETH_USDT_15m.csv')
