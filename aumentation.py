import pandas as pd
import random
import re

class DataAugmenter:
    """
    Módulo de Triplicación Sintética.
    Convierte 1 fila de datos en 3 variantes para robustecer el entrenamiento.
    """

    def __init__(self):
        # Mapeo de Sinónimos (Fonético <-> Logograma)
        # Esto enseña al modelo que son intercambiables.
        self.synonyms = {
            "kaspum": "KÙ.BABBAR",     # Plata
            "KÙ.BABBAR": "kaspum",
            "hurāṣum": "KÙ.GI",        # Oro
            "KÙ.GI": "hurāṣum",
            "annakum": "AN.NA",        # Estaño
            "AN.NA": "annakum",
            "tamkārum": "DAM.GÀR",     # Mercader
            "DAM.GÀR": "tamkārum",
            "qiptum": "QÍ.IP.TUM",     # Préstamo/Confianza
            "šumma": "BE-MA",          # Si...
            "DUMU": "mārum",           # Hijo
            "mārum": "DUMU"
        }

    def _variant_synonym(self, text):
        """
        Variante 1: Reemplazo Semántico.
        Busca palabras clave y las cambia por su equivalente (Logograma/Fonético).
        """
        tokens = text.split()
        new_tokens = []
        changed = False
        
        for t in tokens:
            # Quitamos signos de puntuación para buscar en el diccionario
            clean_t = re.sub(r'[^\w]', '', t)
            
            # Si existe sinónimo y el azar lo decide (50%), lo cambiamos
            if clean_t in self.synonyms and random.random() > 0.5:
                # Recuperamos el sinónimo
                syn = self.synonyms[clean_t]
                new_tokens.append(syn)
                changed = True
            else:
                new_tokens.append(t)
                
        return " ".join(new_tokens) if changed else None

    def _variant_damage(self, text):
        """
        Variante 2: Simulación de Daño (Lacunae Injection).
        Elimina aleatoriamente una palabra para simular una tablilla rota.
        Esto entrena al modelo para inferir contexto.
        """
        tokens = text.split()
        if len(tokens) < 3: return None # No romper frases muy cortas
        
        # Elegir un índice al azar para romper
        idx_to_break = random.randint(0, len(tokens) - 1)
        tokens[idx_to_break] = "<BROKEN>"
        
        return " ".join(tokens)

    def triplicate_dataset(self, input_path, output_path):
        print(f"🧬 INICIANDO TRIPLICACIÓN SINTÉTICA DE DATOS...")
        print(f"   In: {input_path}")
        
        try:
            df = pd.read_csv(input_path)
        except FileNotFoundError:
            print("❌ No encuentro el archivo limpio. Ejecuta generate_clean_data.py primero.")
            return

        new_rows = []
        original_count = len(df)

        print("   Generando variantes...")
        for _, row in df.iterrows():
            text = str(row.get('clean_text', ''))
            trans = row.get('translation', '')
            
            # 1. EL ORIGINAL (Baseline)
            new_rows.append({
                'clean_text': text,
                'translation': trans,
                'aug_type': 'original'
            })
            
            # 2. VARIANTE SEMÁNTICA (Synonym Swap)
            syn_text = self._variant_synonym(text)
            if syn_text:
                new_rows.append({
                    'clean_text': syn_text,
                    'translation': trans, # La traducción es la misma
                    'aug_type': 'synthetic_synonym'
                })
                
            # 3. VARIANTE DE DAÑO (Noise Injection)
            dmg_text = self._variant_damage(text)
            if dmg_text:
                new_rows.append({
                    'clean_text': dmg_text,
                    'translation': trans, # La traducción es la misma
                    'aug_type': 'synthetic_damage'
                })

        # Crear DataFrame Final
        df_augmented = pd.DataFrame(new_rows)
        
        # Guardar
        df_augmented.to_csv(output_path, index=False)
        
        final_count = len(df_augmented)
        print(f"✅ ¡PROCESO COMPLETADO!")
        print(f"   Originales: {original_count}")
        print(f"   Sintéticos Generados: {final_count - original_count}")
        print(f"   Total Dataset Training: {final_count}")
        print(f"   Archivo guardado en: {output_path}")

# Bloque para probarlo individualmente
if __name__ == "__main__":
    # Asegúrate de que las rutas coincidan con tu config.py
    INPUT = "input/processed/preprocessing.csv"
    OUTPUT = "input/processed/train_augmented.csv"
    
    augmenter = DataAugmenter()
    augmenter.triplicate_dataset(INPUT, OUTPUT)