import pandas as pd
import pandas_ta as ta


class Strategy:
    def __init__(self):
        self.estado_actual = {} #Memoria para no repetir alertas

    def analizar(self, simbolo, precio_actual, historial):
        # Paso 0: Inicializar si es moneda nueva
        if simbolo not in self.estado_actual:
            self.estado_actual[simbolo] = 'BUSCANDO_COMPRA'

        # Paso 1: Generar propuestas (Lógica simple: vender si el precio sube, comprar si baja)
        propuesta = self._generar_propuesta(historial,simbolo) 

        if not propuesta: 
            return None 
        # --- AQUÍ LA LÓGICA DE MEMORIA ---
        # Si el RSI dice COMPRA y el bot está esperando para comprar...
        if propuesta == 'COMPRA' and self.estado_actual[simbolo] == 'BUSCANDO_COMPRA': #Aún no compra por eso está buscando compra
            # (Aquí irán los filtros de IA/Estadística luego)
            self.estado_actual[simbolo] = 'BUSCANDO_VENTA' # Cambiamos el chip
            return f"🟢 COMPRA!: {simbolo} | Precio: {precio_actual} " # Compra ESTO/CON_ESTO 

        # Si el RSI dice VENTA y el bot ya tenía algo para vender...
        if propuesta == 'VENTA' and self.estado_actual[simbolo] == 'BUSCANDO_VENTA':
            # (Aquí irán los filtros de IA/Estadística luego)
            self.estado_actual[simbolo] = 'BUSCANDO_COMPRA' # Cambiamos el chip
            return f"🔴 VENDE!: {simbolo} | Precio: {precio_actual}"
        
        return None # Si el RSI dice compra pero ya compramos, no hacemos nada        
        
        # Paso 2: Filtro Estadístico (¿Es probable que gane?)
        # Paso 3: Filtro de IA (¿Qué dice el modelo?)
        # Paso 4: Filtro de Riesgo (¿Cuánto arriesgo?)
        
    
    def _generar_propuesta(self, historial,simbolo):
        # Extraer los precios de cierre del historial
        cierres = [vela[4] for vela in historial] 
        df = pd.DataFrame(cierres, columns=['Close'])

        # Calcular el RSI con un periodo de 14
        rsi_serie = ta.rsi(df['Close'], length=14)

        if rsi_serie is None or len(rsi_serie) < 1:
            return None # No hay suficiente información para calcular el RSI (Caso Base)
        
        ultimo_rsi = rsi_serie.iloc[-1]
        # print del RSI con el símbolo 
        print(f"RSI de {simbolo}: {ultimo_rsi:.2f}")

        if ultimo_rsi < 30:
            return 'COMPRA'
        elif ultimo_rsi > 70:
            return 'VENTA'
        return None # No hay señal clara

    # def _filtro_estadistico(self, precio_actual, historial):
    #     # Aquí calculas: "¿Este movimiento es normal o exagerado?"
    #     # Usas el historial para comparar.
    #     return True # Por ahora dejamos que pase todo
    
    # def _filtro_ia(self, precio_actual, historial):
    #     # Aquí irá tu modelo de Machine Learning en el futuro.
    #     return True # Por ahora dejamos que pase todo
