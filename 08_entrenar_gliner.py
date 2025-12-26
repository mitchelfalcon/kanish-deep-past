import json
import torch
from gliner import GLiNERConfig, GLiNER
from random import shuffle

# --- CONFIGURACIÓN ---
MODELO_BASE = "urchade/gliner_small-v2.1" # Ligero y potente
CARPETA_SALIDA = "models/kanish_ner_gliner"
LABELS = ["person", "location", "goods"] # Las etiquetas que pidió la Hoja de Ruta

def cargar_datos_entrenamiento():
    """
    Aquí deberías cargar tus 1.500 textos etiquetados desde un JSON.
    Formato esperado: Lista de diccionarios con 'tokenized_text' y 'ner'.
    """
    # --- SIMULACIÓN DE DATOS (Para que el script corra ya mismo) ---
    print("⚠️ Usando datos simulados. Reemplaza esto con tu json real.")
    dataset = [
        {
            "tokenized_text": ["um-ma", "Puzur-Aššur", "-ma", "a-na", "En-lil-ba-ni", "qbi-ma"],
            "ner": [[1, 1, "person"], [4, 4, "person"]] # Índices start, end, label
        },
        {
            "tokenized_text": ["10", "manā", "kù-babbar", "i-na", "Kaniš", "al-qé"],
            "ner": [[2, 2, "goods"], [4, 4, "location"]]
        }
    ]
    # Multiplicamos los datos para simular volumen
    return dataset * 50 

def entrenar_gliner():
    print(f"--- 🕵️ INICIANDO ENTRENAMIENTO GLiNER ---")
    
    # 1. Cargar datos
    datos = cargar_datos_entrenamiento()
    shuffle(datos)
    split = int(len(datos) * 0.9)
    train_data = datos[:split]
    eval_data = datos[split:]
    
    print(f"   > Datos de entrenamiento: {len(train_data)}")
    print(f"   > Datos de evaluación: {len(eval_data)}")

    # 2. Inicializar Modelo
    # Usamos CUDA (GPU) si está disponible, si no CPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"   > Usando dispositivo: {device}")
    
    model = GLiNER.from_pretrained(MODELO_BASE)
    model.to(device)

    # 3. Configurar Hiperparámetros (Optimizados para Low-Resource)
    # GLiNER se entrena diferente a BERT, no usa Trainer standard de HF
    # Aquí simulamos el loop de fine-tuning (simplified wrapper)
    
    # NOTA: La librería GLiNER tiene métodos específicos de fine-tuning.
    # Esta es la implementación estándar para v2.
    from gliner.training import Trainer, TrainingArguments
    
    args = TrainingArguments(
        output_dir=CARPETA_SALIDA,
        learning_rate=5e-6,        # Tasa baja para no olvidar lo pre-entrenado
        weight_decay=0.01,
        others_lr=1e-5,
        others_weight_decay=0.01,
        num_train_epochs=3,        # Pocas épocas para evitar overfitting
        batch_size=4,
        save_steps=100,
        save_total_limit=2,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_data,
        eval_dataset=eval_data,
        tokenizer=model.tokenizer,
    )

    # 4. Entrenar
    print("🏋️ Entrenando... (Esto tomará tiempo dependiendo de tu GPU)")
    trainer.train()
    
    # 5. Guardar
    model.save_pretrained(CARPETA_SALIDA)
    print(f"✅ Modelo GLiNER guardado en: {CARPETA_SALIDA}")

if __name__ == "__main__":
    entrenar_gliner()