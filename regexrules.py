# src/preprocessing.py
import re
from .config import CLITICS

class KanishRefinery:
    """
    Motor de Limpieza y Normalización para Deep Learning.
    Aplica reglas Regex estrictas para separar morfología.
    """
    def __init__(self):
        # 1. Regex para Logogramas (Mayúsculas con puntos: DUMU.ZI)
        # Queremos protegerlos para que NO se separen.
        self.regex_logogram = re.compile(r'\b([A-ZŠṢṬÁÉÍÚÀÈÌÙÂÊÎÛ]+\.[A-ZŠṢṬÁÉÍÚÀÈÌÙÂÊÎÛ\.]+)\b')
        
        # 2. Regex para Clíticos (Guion + Clítico al final de palabra)
        # -(ma|ni|ku...) seguido de fin de palabra o espacio
        pattern = r'-(' + '|'.join(CLITICS) + r')\b'
        self.regex_clitic = re.compile(pattern, re.IGNORECASE)
        
        # 3. Regex para Signos Perdidos (Cualquier cosa entre corchetes con x o puntos)
        self.regex_broken = re.compile(r'\[[x\.\s]+\]|\(x+\)|x{2,}', re.IGNORECASE)

    def process_text(self, text):
        if not isinstance(text, str): return ""
        
        # PASO A: Normalizar Signos Rotos -> <BROKEN>
        # Esto evita que la IA alucine intentando leer "[x x x]"
        clean_text = self.regex_broken.sub(' <BROKEN> ', text)
        
        # PASO B: Separación de Clíticos (Logragrams vs Cicliclos/Clíticos)
        # Transformamos "iqbi-ma" -> "iqbi -ma"
        # El espacio extra ayuda al tokenizador de Deep Learning (Byte-Pair Encoding)
        clean_text = self.regex_clitic.sub(r' -\1', clean_text)
        
        # PASO C: Limpieza de Logogramas
        # Aquí la estrategia es sutil: Los logogramas YA tienen puntos (É.GAL).
        # Nos aseguramos de NO reemplazar esos puntos por espacios.
        # Solo reemplazamos puntos y guiones que NO sean parte de logogramas o clíticos.
        
        # Normalizar espacios múltiples
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text

    def unify_directions(self, text):
        """
        Placeholder para la lógica SOV -> SVO (Unifies Directions).
        En esta fase de limpieza, preparamos los tokens.
        El reordenamiento real requiere un análisis sintáctico (POS Tagging).
        """
        # Por ahora, devolvemos el texto limpio. 
        # Si tuvieras etiquetas gramaticales, aquí harías el 'swap'.
        return text