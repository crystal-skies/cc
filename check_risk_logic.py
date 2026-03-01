import pandas as pd
from risk_manager import RiskManager

def test_real_data():
    # 1. Cargar datos procesados
    # Asegúrate de que las rutas sean correctas para tu sistema
    try:
        df_btc = pd.read_csv("cryptoml/BTC_USDT_15m.csv")
        df_eth = pd.read_csv("cryptoml/dataset_para_el_juezETH.csv")
        print("✅ CSVs cargados correctamente.")
    except Exception as e:
        print(f"❌ Error al cargar los archivos: {e}")
        return

    # Inicializar el RiskManager con tu SL del 1.25% (post-comisión)
    rm = RiskManager(stop_loss_pct=0.0125) 
    
    saldo_simulado = 20.0
    
    # Buscar señales donde el RSI sea menor a 35
    señales_potenciales = df_eth[(df_eth['RSI'] < 35)].index
    
    print(f"Analizando {len(señales_potenciales)} señales de compra potenciales en ETH...\n")

    for i in señales_potenciales[:10]: # Probamos las primeras 10 señales encontradas
        # VALIDACIÓN: Necesitamos al menos 100 velas previas para los cálculos (SMA20, ATR, etc.)
        if i < 100:
            continue
            
        # Extraer bloques de historial para el RiskManager
        datos_btc = df_btc.iloc[i-100:i+1] # i+1 para incluir la vela actual
        datos_eth = df_eth.iloc[i-100:i+1]
        
        # Simulamos la confianza que daría tu IA (74% según tu Random Forest)
        confianza_ia = 0.74 
        
        # Llamada al método corregido 'get_verdict'
        veredicto = rm.get_verdict(
            current_balance=saldo_simulado,
            df_coin=datos_eth,
            df_btc=datos_btc,
            ia_confidence=confianza_ia,
            symbol="ETH/USDT"
        )
        
        # Formatear la salida para que sea legible
        status = veredicto['decision']
        motivo = veredicto.get('reason', 'N/A')
        monto = veredicto.get('size', 0)
        atr_info = veredicto.get('atr', 'N/A')
        
        print(f"Vela: {i} | RSI: {df_eth.loc[i, 'RSI']:.2f}")
        if status == "PROCEED":
            print(f"  ✅ {status} | Invertir: ${monto} | ATR: {atr_info}")
        else:
            print(f"  ❌ {status} | Motivo: {motivo}")
        print("-" * 50)

if __name__ == "__main__":
    test_real_data()