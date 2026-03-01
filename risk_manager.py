import pandas as pd
import numpy as np

class RiskManager:
    def __init__(self, stop_loss_pct=0.015, min_trade_size=10.0, survival_floor=11.0):
        self.sl_pct = stop_loss_pct
        self.min_size = min_trade_size
        self.survival_floor = survival_floor
    
    def _calculate_atr_pct(self, df):
        try:
            if len(df) < 15: return 0.0
            
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            atr = true_range.rolling(14).mean().iloc[-1]
            
            return (atr / df['close'].iloc[-1])
        except Exception:
            return 0.0
    
    def _get_correlation(self, df_coin, df_btc):
        try:
            # Aseguramos que usamos los mismos índices finales
            if len(df_coin) < 31 or len(df_btc) < 31: return 0.0
            
            returns_coin = df_coin['close'].pct_change().tail(30)
            returns_btc = df_btc['close'].pct_change().tail(30)
            
            correlation = returns_coin.corr(returns_btc)
            return correlation if not np.isnan(correlation) else 0.0
        except Exception:
            return 0.0
    
    def get_verdict(self, current_balance, df_coin, df_btc, ia_confidence, symbol):
        """
        Calcula si se debe operar. 
        Nota: Cambié 'get_veredict' a 'get_verdict' y corregí los nombres de las llaves.
        """
        # 0. Validación de datos mínimos
        if len(df_coin) < 20 or len(df_btc) < 20:
            return {"decision": "VETO", "reason": "Historial insuficiente", "size": 0}

        # 1. Chequeo de supervivencia
        if current_balance < self.survival_floor:
            return {"decision": "VETO", "reason": f"Balance ({current_balance}) por debajo del piso", "size": 0}
        
        # 2. Análisis de Volatilidad (Filtro de Ruido)
        atr_pct = self._calculate_atr_pct(df_coin)
        # Si el mercado se mueve más del 80% de nuestro SL por puro ruido, vetamos.
        if atr_pct >= (self.sl_pct * 0.8):
            return {"decision": "VETO", "reason": f"Ruido alto ({atr_pct:.2%}) > Limite ({self.sl_pct*0.8:.2%})", "size": 0}
        
        # 3. Análisis de correlación (BTC como ancla)
        if symbol != 'BTC/USDT':
            corr = self._get_correlation(df_coin, df_btc)
            # Tendencia de BTC (Media de 20 periodos)
            btc_sma20 = df_btc['close'].rolling(20).mean().iloc[-1]
            btc_trend_down = df_btc['close'].iloc[-1] < btc_sma20
            
            if corr > 0.7 and btc_trend_down:
                return {"decision": "VETO", "reason": f"Alta correlacion ({corr:.2f}) con BTC bajista", "size": 0}
        
        # 4. Position Sizing Dinámico (CORREGIDO)
        # Si la confianza es muy alta (>85%), usamos más capital.
        # Si es media (70-85%), usamos el mínimo.
        # Si es baja (<70%), vetamos.
        if ia_confidence >= 0.85:
            size = min(current_balance, 20.0) 
        elif ia_confidence >= 0.70:
            size = self.min_size
        else:
            return {"decision": "VETO", "reason": f"Confianza IA baja ({ia_confidence:.2f})", "size": 0}
        
        return {
            "decision": "PROCEED",
            "size": round(size, 2),
            "reason": "Condiciones optimas",
            "atr": f"{atr_pct:.2%}"
        }