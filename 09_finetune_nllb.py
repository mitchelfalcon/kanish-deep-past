import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForSeq2SeqLM, 
    AutoTokenizer, 
    Seq2SeqTrainingArguments, 
    Seq2SeqTrainer,
    DataCollatorForSeq2Seq
)
from peft import get_peft_model, LoraConfig, TaskType

# --- CONFIGURACIÓN ---
MODELO_ID = "facebook/nllb-200-distilled-600M"
CARPETA_SALIDA = "models/kanish_translator_nllb"
DATASET_CSV = "output/dataset_aumentado/corpus_aumentado.csv" # Generado en Sprint 1

# Códigos de idioma NLLB (Akkadian no existe oficial, usamos un proxy o código reservado)
# Truco: Usaremos 'akk_Latn' (si existiera) o reusaremos un código raro como 'kmr_Latn' 
# y le enseñaremos que eso es Acadio. Para este ejemplo usaremos inglés estándar como target.
SRC_LANG = "akk_Latn" # Definimos nuestro propio token source
TGT_LANG = "eng_Latn" 

def main():
    print("--- 🗣️ INICIANDO FINE-TUNING NLLB-200 CON LoRA ---")
    
    # 1. Cargar Dataset (El CSV del Sprint 1)
    if not os.path.exists(DATASET_CSV):
        print(f"❌ Error: No encuentro {DATASET_CSV}. Ejecuta el Sprint 1 primero.")
        return

    dataset = load_dataset("csv", data_files=DATASET_CSV)
    # Dividir Train/Test
    dataset = dataset["train"].train_test_split(test_size=0.1)
    
    print(f"   > Train set: {len(dataset['train'])}")
    print(f"   > Test set: {len(dataset['test'])}")

    # 2. Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODELO_ID, src_lang=SRC_LANG, tgt_lang=TGT_LANG)

    def preprocess_function(examples):
        inputs = [ex for ex in examples["transliteracion"]]
        targets = [ex for ex in examples["traduccion"]]
        
        model_inputs = tokenizer(inputs, max_length=128, truncation=True)
        labels = tokenizer(targets, max_length=128, truncation=True)
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    tokenized_datasets = dataset.map(preprocess_function, batched=True)

    # 3. Modelo Base + LoRA (El secreto de eficiencia)
    print("   > Cargando modelo y aplicando adaptadores LoRA...")
    model = AutoModelForSeq2SeqLM.from_pretrained(MODELO_ID)
    
    peft_config = LoraConfig(
        task_type=TaskType.SEQ_2_SEQ_LM, 
        inference_mode=False, 
        r=16,            # Rango de la matriz (mayor = más inteligente pero más lento)
        lora_alpha=32, 
        lora_dropout=0.1
    )
    
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters() # Verás que entrenamos solo el ~1% de params

    # 4. Configuración de Entrenamiento (Símil SageMaker)
    args = Seq2SeqTrainingArguments(
        output_dir=CARPETA_SALIDA,
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16, # Ajustar según memoria GPU
        per_device_eval_batch_size=16,
        weight_decay=0.01,
        save_total_limit=3,
        num_train_epochs=5,
        predict_with_generate=True,
        fp16=True, # Usar media precisión (muy rápido en GPUs modernas)
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["test"],
        tokenizer=tokenizer,
        data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
    )

    # 5. Entrenar
    print("🚀 Despegando entrenamiento...")
    trainer.train()

    # 6. Guardar
    model.save_pretrained(CARPETA_SALIDA)
    tokenizer.save_pretrained(CARPETA_SALIDA)
    print(f"✅ Traductor Kanish guardado en: {CARPETA_SALIDA}")

if __name__ == "__main__":
    main()