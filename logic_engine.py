import joblib
import pandas as pd
import pandas_ta as ta

class Strategy:
    def __init__(self):
        self.memoria = {} # Para no repetir compras/ventas
        self.juez = joblib.load('cryptoml/juez_binario.pkl') # Cargamos el cerebro

    def analizar(self, simbolo, precio_actual, historial):
        # 0. Preparación: Convertir historial en indicadores
        df = self._calcular_indicadores(historial)
        if df.empty: return None
        
        # --- LA LÍNEA DE ENSAMBLAJE (Chips) ---
        
        # PASO 1: Chip Técnico (¿Hay señal de RSI?)
        propuesta = self._chip_tecnico_rsi(df)
        if not propuesta: return None 

        # PASO 2: Chip de Memoria (¿Ya compré/vendí antes?)
        if not self._chip_memoria_estado(simbolo, propuesta):
            return None

        # PASO 3: Chip de IA (¿El Juez aprueba la propuesta?)
        if not self._chip_ia_juez(df, propuesta):
            return None

        # --- SI LLEGÓ AQUÍ, LA OPERACIÓN ES VÁLIDA ---
        return self._ejecutar_accion(simbolo, precio_actual, propuesta)

    # =========================================================
    # DEFINICIÓN DE LOS "CHIPS" (Módulos independientes)
    # =========================================================

    def _calcular_indicadores(self, historial):
        """ Sincronizado exactamente con processor.py """
        df = pd.DataFrame(historial, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
        
        # 1. RSI (14)
        df['RSI'] = ta.rsi(df['close'], length=14)
        
        # 2. ATR (14)
        df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        
        # 3. Volumen Relativo (20)
        df['Volumen_Relativo'] = df['volume'] / df['volume'].rolling(window=20).mean()
        
        # 4. Distancia SMA 200
        sma200 = ta.sma(df['close'], length=200)
        df['distancia_sma200'] = (df['close'] - sma200) / sma200
        
        # 5. Tendencia Superior (SMA 50 diff 5)
        sma50 = ta.sma(df['close'], length=50)
        df['tendencia_superior'] = sma50.diff(periods=5)
        
        # 6. Momentum (ROC 10)
        df['momentum'] = ta.roc(df['close'], length=10)
        
        # 7. Distancia EMMA 200
        emma200 = ta.ema(df['close'], length=200)
        df['distancia_emma200'] = (df['close'] - emma200) / emma200
        
        # 8. Tendencia Macro (EMA 800)
        emma800 = ta.ema(df['close'], length=800)
        df['tendencia_macro'] = (df['close'] > emma800).astype(int)
        
        # PRICE ACTION (Con factor 1e-9 de tu processor.py)
        rango_total = df['high'] - df['low']
        cuerpo = (df['close'] - df['open']).abs()
        
        # 9. Calidad cuerpo
        df['calidad_cuerpo'] = cuerpo / (rango_total + 1e-9)
        
        # 10. Mecha superior
        df['mecha_superior'] = (df['high'] - df[['close', 'open']].max(axis=1)) / (rango_total + 1e-9)
        
        # 11. Mecha inferior
        df['mecha_inferior'] = (df[['close', 'open']].min(axis=1) - df['low']) / (rango_total + 1e-9)
        
        # 12. Volatilidad Relativa
        df['volatilidad_rel'] = df['ATR'] / df['close']
        
        # 13. RSI Lento (Periodo 50 según tu entrenamiento)
        df['RSI_lento'] = ta.rsi(df['close'], length=50)
        
        return df.dropna()

    def _chip_ia_juez(self, df, propuesta):
        """ El ML usa las 13 variables en el orden y formato exactos """
        
        # Definimos las columnas exactas que usó el procesador para entrenar
        columnas_features = [
            'RSI', 'ATR', 'Volumen_Relativo', 'distancia_sma200', 
            'tendencia_superior', 'momentum', 'distancia_emma200', 
            'tendencia_macro', 'calidad_cuerpo', 'mecha_superior', 
            'mecha_inferior', 'volatilidad_rel', 'RSI_lento'
        ]
        
        # Extraemos la última fila como DataFrame para mantener nombres de columnas
        features_df = df.iloc[-1:][columnas_features]
        
        try:
            # Predicción con nombres de columnas (Evita el UserWarning)
            probabilidad = self.juez.predict_proba(features_df)[0][1]
            
            # Umbral de confianza
            if probabilidad > 0.70:
                print(f"Juez aprueba {propuesta} con {probabilidad*100:.1f}% de confianza.")
                return True
            else:
                # print(f"Juez rechaza {propuesta}: Confianza insuficiente ({(probabilidad*100):.1f}%)")
                return False
        except Exception as e:
            print(f"Error en Chip IA: {e}")
            return False

    def _chip_tecnico_rsi(self, df):
        """ Devuelve propuesta según el RSI (Lógica idéntica al disparador del entrenamiento) """
        ultimo_rsi = df.iloc[-1]['RSI']
        if ultimo_rsi < 35: return 'COMPRA'
        if ultimo_rsi > 65: return 'VENTA'
        return None

    def _chip_memoria_estado(self, simbolo, propuesta):
        """ Evita duplicados """
        if simbolo not in self.memoria:
            self.memoria[simbolo] = 'BUSCANDO_COMPRA'

        if propuesta == 'COMPRA' and self.memoria[simbolo] == 'BUSCANDO_COMPRA':
            return True
        if propuesta == 'VENTA' and self.memoria[simbolo] == 'BUSCANDO_VENTA':
            return True
        return False

    def _ejecutar_accion(self, simbolo, precio_actual, propuesta):
        """ Actualiza estado y retorna mensaje """
        if propuesta == 'COMPRA':
            self.memoria[simbolo] = 'BUSCANDO_VENTA'
            return f"🟢 COMPRA APROBADA: {simbolo} a {precio_actual}"
        else:
            self.memoria[simbolo] = 'BUSCANDO_COMPRA'
            return f"🔴 VENTA APROBADA: {simbolo} a {precio_actual}" 