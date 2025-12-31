import re
from typing import List, Tuple

class CuneiformTokenizer:
    """
    Implementa la lógica SDA-02: Tokenizador Morfológico Híbrido.
    Maneja la distinción entre Logogramas (É.GAL) y Morfemas (be-lí-ni).
    """

    def __init__(self):
        # Regex patterns
        self.noise_patterns = [
            (r'\d+\.', ''),          # Elimina números de línea (1., 2.)
            (r'\(.*?\)', ''),        # Elimina comentarios entre paréntesis (filtro básico)
            (r'\s+', ' '),           # Normaliza espacios
            (r'^\s+|\s+$', '')       # Trim
        ]
        
        # Tokens especiales
        self.damaged_token = "[DMG]"
        self.missing_token = "[MISSING]"

    def clean_noise(self, raw_text: str) -> str:
        """
        Algoritmo de Limpieza (The Scrubber).
        """
        clean_text = raw_text
        for pattern, replacement in self.noise_patterns:
            clean_text = re.sub(pattern, replacement, clean_text)
        
        # Estandarización de daños (x -> [DMG], ... -> [MISSING])
        clean_text = clean_text.replace('x', self.damaged_token)
        clean_text = clean_text.replace('[...]', self.missing_token)
        
        return clean_text.strip()

    def tokenize(self, text: str) -> List[str]:
        """
        Lógica de Preservación vs. Separación.
        1. Preserva uniones por '.' (Logogramas complejos).
        2. Separa uniones por '-' (Clíticos y sufijos).
        """
        # Paso 1: Dividir por espacios para obtener bloques de palabras
        word_blocks = text.split(' ')
        final_tokens = []

        for block in word_blocks:
            # Si el bloque contiene guiones, es candidato a separación morfológica
            if '-' in block:
                # Separamos por guión
                sub_parts = block.split('-')
                for part in sub_parts:
                    if part: # Evitar vacíos
                        final_tokens.append(part)
            else:
                # Si contiene puntos (É.GAL) o es simple, se mantiene unido
                if block:
                    final_tokens.append(block)
        
        return final_tokens

    def analyze_structure(self, tokens: List[str]) -> List[Tuple[str, str]]:
        """
        Etiqueta preliminarmente los tokens (Root vs Suffix) basado en heurística simple.
        (Esta lógica se expandiría con la Tabla D: Morphology_Offsets).
        """
        analysis = []
        for t in tokens:
            tag = "UNKNOWN"
            if '.' in t:
                tag = "LOGOGRAM_COMPLEX"
            elif t.isupper():
                tag = "LOGOGRAM_SIMPLE"
            elif t in ["[DMG]", "[MISSING]"]:
                tag = "META"
            else:
                tag = "PHONETIC/MORPH"
            analysis.append((t, tag))
        return analysis