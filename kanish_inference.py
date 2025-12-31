# kanish_inference.py
import pandas as pd
import sys
import os

# Añadir src al path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from src.kanish_engine import KanishInferenceEngine
from src.config import PATHS

def run_inference_pipeline():
    print("--- 🏛️ KANISH SYSTEM: INFERENCE PROTOCOL ---")
    
    # 1. Cargar Datos de Prueba (Kaggle Test)
    try:
        df_test = pd.read_csv(PATHS['RAW_TEST'])
        # Asegurarnos de usar la columna correcta
        col_text = 'transliteration' if 'transliteration' in df_test.columns else 'text'
        texts = df_test[col_text].tolist()
        ids = df_test['id'].tolist() if 'id' in df_test.columns else range(len(texts))
    except Exception as e:
        print(f"❌ Error cargando test data: {e}")
        return

    # 2. Iniciar Motor
    engine = KanishInferenceEngine() # Cargará el modelo entrenado si existe
    
    results = []
    print(f"🔄 Procesando {len(texts)} tablillas...")
    
    for i, text in enumerate(texts):
        # Limpieza rápida en tiempo de inferencia (si es necesario)
        # text = refinery.process_text(text) <-- Opcional si ya está limpio
        
        output = engine.predict(text)
        
        # Lógica de Marduk: Si la confianza es muy baja, marcar para revisión humana
        # (O en Kaggle, quizás usar un fallback seguro)
        status = "APPROVED" if output['confidence'] > 0.7 else "FLAGGED"
        
        results.append({
            'id': ids[i],
            'translation': output['translation'],
            # Campos extra para auditoría (no se envían a Kaggle, pero sirven para ti)
            'confidence': output['confidence'],
            'marduk_flags': str(output['flags'])
        })
        
        if i % 100 == 0:
            print(f"   [{i}/{len(texts)}] Última: {output['translation']} | Score: {output['confidence']}")

    # 3. Guardar Submission
    df_submission = pd.DataFrame(results)
    
    # Para Kaggle solo necesitamos id y translation
    submission_path = "submission.csv"
    df_submission[['id', 'translation']].to_csv(submission_path, index=False)
    
    # Guardar reporte de auditoría completo
    df_submission.to_csv("audit_report_marduk.csv", index=False)
    
    print(f"\n✅ Misión Cumplida. Archivo generado: {submission_path}")
    print(f"🛡️ Registros marcados por Marduk: {len(df_submission[df_submission['confidence'] < 0.7])}")

if __name__ == "__main__":
    run_inference_pipeline()