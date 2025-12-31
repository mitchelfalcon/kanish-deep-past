# src/neural_motor.py
import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainingArguments, Seq2SeqTrainer, DataCollatorForSeq2Seq
from datasets import Dataset
import pandas as pd

class NeuralMotor:
    def __init__(self, model_name="facebook/nllb-200-distilled-600M"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, src_lang="akk_Latn", tgt_lang="eng_Latn")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        
    def train(self, data_path, output_dir="models/nllb-kanish-finetuned"):
        print("🧠 Inicializando Neural Motor (Training Mode)...")
        
        # 1. Cargar Data Limpia
        df = pd.read_csv(data_path)
        # Asegurarnos de que no haya nulos
        df = df.dropna(subset=['clean_text', 'translation'])
        
        # Convertir a formato HuggingFace
        dataset = Dataset.from_pandas(df[['clean_text', 'translation']])
        split = dataset.train_test_split(test_size=0.1)
        
        # 2. Tokenización
        def preprocess(examples):
            inputs = examples["clean_text"]
            targets = examples["translation"]
            model_inputs = self.tokenizer(inputs, max_length=128, truncation=True)
            labels = self.tokenizer(targets, max_length=128, truncation=True)
            model_inputs["labels"] = labels["input_ids"]
            return model_inputs

        tokenized_data = split.map(preprocess, batched=True)

        # 3. Configurar Entrenamiento
        args = Seq2SeqTrainingArguments(
            output_dir=output_dir,
            evaluation_strategy="epoch",
            learning_rate=2e-5,
            per_device_train_batch_size=8, # Ajustar según tu VRAM
            num_train_epochs=3,
            weight_decay=0.01,
            save_total_limit=2,
            predict_with_generate=True,
            fp16=torch.cuda.is_available() # Usar GPU si existe
        )

        trainer = Seq2SeqTrainer(
            model=self.model,
            args=args,
            train_dataset=tokenized_data["train"],
            eval_dataset=tokenized_data["test"],
            tokenizer=self.tokenizer,
            data_collator=DataCollatorForSeq2Seq(self.tokenizer, model=self.model),
        )

        print("🚀 Despegando Entrenamiento...")
        trainer.train()
        
        print(f"💾 Guardando modelo en {output_dir}")
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)