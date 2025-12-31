# src/marduk_validator.py
import re

class MardukValidator:
    """
    El Juez Neuro-Simbólico.
    Valida la consistencia lógica entre Fuente (Acadio) y Destino (Inglés).
    """
    def __init__(self):
        # Mapeos críticos de consistencia
        self.num_map = {'1': 'one', '2': 'two', '3': 'three', '10': 'ten', '5': 'five'}
        self.entity_map = {
            'KÙ.BABBAR': ['silver', 'money'],
            'KÙ.GI': ['gold'],
            'AN.NA': ['tin', 'lead'],
            'TÚG': ['textile', 'garment', 'cloth'],
            'DUMU': ['son']
        }

    def extract_numbers(self, text):
        return re.findall(r'\d+', text)

    def validate(self, source_text, translated_text):
        """
        Retorna un score de confianza (0.0 a 1.0) y flags de advertencia.
        """
        warnings = []
        score = 1.0
        
        src_lower = source_text.lower()
        trg_lower = translated_text.lower()

        # 1. Validación Numérica (Aritmética Sagrada)
        src_nums = self.extract_numbers(source_text)
        for num in src_nums:
            # Si hay un "10" en acadio, debe haber un "10" o "ten" en inglés
            num_word = self.num_map.get(num, num) # fallback al mismo digito
            if num not in translated_text and num_word not in trg_lower:
                warnings.append(f"MISSING_NUMBER_{num}")
                score -= 0.3

        # 2. Validación de Mercancías (Ontología)
        for token, expected_words in self.entity_map.items():
            if token in source_text: # Si el logograma está en el original
                # Verificar si alguna de las traducciones esperadas aparece
                match = any(w in trg_lower for w in expected_words)
                if not match:
                    warnings.append(f"MISSING_ENTITY_{token}")
                    score -= 0.2

        # 3. Detector de Alucinación (Longitud)
        # Si la traducción es 3 veces más larga que el original, algo anda mal.
        if len(trg_lower) > len(src_lower) * 4 and len(src_lower) > 5:
             warnings.append("POSSIBLE_HALLUCINATION_LENGTH")
             score -= 0.1

        return max(0.0, score), warnings