import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

def entrenar_chip_ml(archivo_csv):
    # 1. Cargar los datos procesados
    df = pd.read_csv(archivo_csv)
    
    # 2. Seleccionar las evidencias (Features) que el Juez debe evaluar
    features = [
        'RSI', 'ATR', 'Volumen_Relativo', 'distancia_sma200', 
        'tendencia_superior', 'momentum', 'distancia_emma200',
        'tendencia_macro', 'calidad_cuerpo', 'mecha_superior',
        'mecha_inferior', 'volatilidad_rel', 'RSI_lento'
    ]

    X = df[features]
    y = df['target'] # Éxito (1) o Fracaso (0)

    # 3. Dividir en: Datos de estudio (80%) y Datos de examen final (20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("🧠 El Juez está estudiando los patrones de éxito...")

    # 4. Crear el modelo (Bosque Aleatorio)
    # Usamos class_weight='balanced' porque hay muchos más fracasos que éxitos
    model = RandomForestClassifier(
        n_estimators=200, 
        max_depth=15, 
        class_weight='balanced', 
        random_state=42
    )
    
    model.fit(X_train, y_train)

    # 5. EXAMEN: ¿Qué tan bueno es el Juez?
    probabilidades = model.predict_proba(X_test)[:, 1] # Probabilidad de que sea Clase 1 (Éxito)
    umbral = 0.85 # Podemos ajustar este umbral para ser más conservadores o agresivos
    y_pred = (probabilidades >= umbral).astype(int) # Convertimos a 0 o 1 según el umbral
    
    print(f"\n--- RESULTADO CON UMBRAL DEL {umbral*100}% ---")
    print(classification_report(y_test, y_pred))

    # 6. IMPORTANCIA DE LAS PISTAS
    # Nos dice qué "chip" de información le sirvió más al Juez
    importancias = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
    print("\n--- PISTAS MÁS IMPORTANTES PARA EL JUEZ ---")
    print(importancias)

    # 7. GUARDAR EL CHIP
    # Este archivo es el que usaremos en el bot real
    joblib.dump(model, 'juez_binario.pkl')
    print("\n✅ Chip de ML fabricado exitosamente: 'juez_binario.pkl'")

if __name__ == "__main__":
    entrenar_chip_ml('dataset_para_el_juez.csv')