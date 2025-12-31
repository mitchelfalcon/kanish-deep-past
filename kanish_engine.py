# src/kanish_engine.py
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from .marduk_validator import MardukValidator

class KanishInferenceEngine:
    def __init__(self, model_path="models/nllb-kanish-finetuned"):
        print(f"⚙️ Cargando Kanish Engine desde {model_path}...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        except:
            print("⚠️ Modelo no encontrado. Usando base facebook/nllb-200-distilled-600M")
            self.tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
            self.model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
            
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        # Instanciar al Juez
        self.marduk = MardukValidator()

    def predict(self, text):
        # 1. Inferencia Neuronal
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        
        # Forzamos que el idioma de salida sea Inglés
        forced_bos_token_id = self.tokenizer.lang_code_to_id["eng_Latn"]
        
        with torch.no_grad():
            generated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                max_length=128,
                num_beams=5 # Beam Search para mejor calidad
            )
            
        translation = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        
        # 2. Validación Simbólica (Marduk)
        confidence, warnings = self.marduk.validate(text, translation)
        
        return {
            "source": text,
            "translation": translation,
            "confidence": confidence,
            "flags": warnings
        }