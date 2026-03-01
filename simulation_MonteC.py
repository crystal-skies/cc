import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# CONFIGURACIÓN DE LA SIMULACIÓN
# ==========================================
CAPITAL_INICIAL = 20.0
WIN_RATE = 0.74          # 74% según tu modelo de IA
PROFIT_NETO = 0.008      # +0.8%
LOSS_NETO = -0.015       # -1.5%
OPERACIONES = 100        # Cantidad de trades por simulación
SIMULACIONES = 1000      # Cantidad de "vidas" o iteraciones de Monte Carlo
UMBRAL_RUINA = 10.0      # Ruina si el capital es <= $10 (50% o min Binance)

def ejecutar_monte_carlo():
    print(f"Iniciando {SIMULACIONES} simulaciones de {OPERACIONES} trades...")
    
    resultados_finales = []
    ruinas = 0
    curvas_equity = []

    # Generar todos los resultados de una vez para velocidad (Matriz de 1000x100)
    # 1 es Éxito, 0 es Fracaso
    rng = np.random.default_rng()
    matriz_trades = rng.choice(
        [1, 0], 
        size=(SIMULACIONES, OPERACIONES), 
        p=[WIN_RATE, 1 - WIN_RATE]
    )

    plt.figure(figsize=(12, 6))

    for i in range(SIMULACIONES):
        balance_actual = CAPITAL_INICIAL
        historial_balance = [balance_actual]
        quebro = False

        for j in range(OPERACIONES):
            resultado = matriz_trades[i, j]
            
            if resultado == 1:
                balance_actual *= (1 + PROFIT_NETO)
            else:
                balance_actual *= (1 + LOSS_NETO)
            
            historial_balance.append(balance_actual)

            # Verificar ruina en cada trade
            if balance_actual <= UMBRAL_RUINA:
                quebro = True

        if quebro:
            ruinas += 1
        
        curvas_equity.append(historial_balance)
        resultados_finales.append(balance_actual)
        
        # Graficar cada curva con transparencia
        color = 'red' if quebro else 'green'
        alpha = 0.05 if not quebro else 0.2
        plt.plot(historial_balance, color=color, alpha=alpha, linewidth=1)

    # --- CÁLCULOS ESTADÍSTICOS ---
    prob_ruina = (ruinas / SIMULACIONES) * 100
    esperanza_matematica = (WIN_RATE * PROFIT_NETO) + ((1 - WIN_RATE) * LOSS_NETO)
    retorno_promedio = (np.mean(resultados_finales) - CAPITAL_INICIAL) / CAPITAL_INICIAL * 100
    mediana_final = np.median(resultados_finales)

    # --- RENDERIZADO DEL GRÁFICO ---
    plt.axhline(y=UMBRAL_RUINA, color='black', linestyle='--', label='Límite de Ruina ($10)')
    plt.axhline(y=CAPITAL_INICIAL, color='blue', linestyle='-', alpha=0.5, label='Capital Inicial')
    plt.title(f"Simulación Monte Carlo: {SIMULACIONES} Escenarios\n(Win Rate: {WIN_RATE*100}% | TP: {PROFIT_NETO*100}% | SL: {LOSS_NETO*100}%)")
    plt.xlabel("Número de Trades")
    plt.ylabel("Capital (USDT)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()

    print("\n--- RESULTADOS DE LA CURVA DE REALIDAD ---")
    print(f"Probabilidad de Ruina: {prob_ruina:.2f}%")
    print(f"Esperanza Matemática por trade: {esperanza_matematica*100:.4f}%")
    print(f"Capital Final Promedio: ${np.mean(resultados_finales):.2f}")
    print(f"Capital Final Mediano: ${mediana_final:.2f}")
    print(f"Retorno Promedio Esperado: {retorno_promedio:.2f}%")
    print(f"Peor escenario registrado: ${np.min(resultados_finales):.2f}")
    print(f"Mejor escenario registrado: ${np.max(resultados_finales):.2f}")
    
    if esperanza_matematica <= 0:
        print("\n ALERTA: La esperanza matemática es negativa o nula. El sistema perderá dinero a largo plazo.")
    elif prob_ruina > 5:
        print("\n ALERTA: La probabilidad de ruina es alta. Necesitas el chip de gestión de riesgos urgentemente.")
    else:
        print("\n El sistema muestra robustez estadística inicial.")

if __name__ == "__main__":
    ejecutar_monte_carlo()