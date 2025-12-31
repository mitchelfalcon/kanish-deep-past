# src/augmentation.py
import pandas as pd
import random
import json

class DataAugmenter:
    """
    Genera datos sintéticos variando logogramas vs fonogramas.
    Ej: "ana Kanesh" -> "a-na Kanesh"
    """
    def __init__(self, cipher_path="config/master_cipher.json"):
        try:
            with open(cipher_path, 'r') as f:
                self.cipher = json.load(f)['registry']
        except:
            self.cipher = {}
            print("⚠️ Cipher no cargado. Augmentation limitada.")

    def augment_text(self, text):
        """Crea una variación del texto original"""
        tokens = text.split()
        new_tokens = []
        changed = False
        
        for t in tokens:
            # Estrategia: Ruido Aleatorio (Simular tabletas dañadas)
            if random.random() < 0.05: # 5% de probabilidad
                new_tokens.append("<BROKEN>")
                changed = True
                continue
            
            # Estrategia: Intercambio Logograma <-> Fonético (Si tuvieramos el mapeo)
            # Aquí simulamos variaciones simples
            new_tokens.append(t)
            
        return " ".join(new_tokens) if changed else None

    def generate_synthetic_dataset(self, df, factor=1):
        """Duplica el dataset aplicando variaciones"""
        print(f"🧬 Iniciando Data Augmentation (Factor x{factor})...")
        synthetic_rows = []
        
        for _, row in df.iterrows():
            orig_text = row.get('clean_text', '')
            orig_trans = row.get('translation', '')
            
            for _ in range(factor):
                aug_text = self.augment_text(orig_text)
                if aug_text:
                    synthetic_rows.append({
                        'clean_text': aug_text,
                        'translation': orig_trans, # La traducción no cambia
                        'source': 'synthetic_augmentation'
                    })
        
        df_aug = pd.DataFrame(synthetic_rows)
        print(f"   + {len(df_aug)} registros sintéticos creados.")
        return pd.concat([df, df_aug], ignore_index=True)