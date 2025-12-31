# src/preprocessing.py
import re

class KanishTokenizer:
    """
    The Refinery: Tokenizador Determinista basado en Reglas (SDA-02).
    Distingue entre uniones semánticas (.) y gramaticales (-).
    """

    def __init__(self):
        # Regex para normalizar signos rotos: [x], [...], (x)
        self.re_broken = re.compile(r'\[x+\]|\[\.+\]|\(x+\)', re.IGNORECASE)
        
        # Regex para separar morfemas conectados por guiones
        # "iqbi-ma" -> "iqbi -ma"
        # Usamos Lookbehind para asegurar que no rompa cosas raras, 
        # pero la regla simple es: guion -> espacio + guion
        self.re_morph = re.compile(r'-')

    def clean_and_tokenize(self, text):
        """
        Transforma transliteración cruda en lista de tokens procesables
        para el motor de Gematría.
        """
        if not isinstance(text, str):
            return []

        # PASO 1: Normalización de Anomalías (Robustness Phase)
        # Reemplazar [...] o [x] por token especial
        text = self.re_broken.sub(' [MISSING] ', text)

        # PASO 2: Tratamiento de Morfemas (Regla SDA-02)
        # Separamos los guiones para aislar sufijos clíticos (-ma, -ni, -su)
        # Ejemplo: "be-lí-ni" -> "be lí -ni" (Depende de tu preferencia, 
        # SDIC-G a veces prefiere mantener la raíz y separar el clítico final)
        
        # Estrategia SDIC-G: El guion es un separador morfológico.
        # Reemplazamos '-' por ' ' (espacio) para que el split() posterior funcione,
        # PERO mantenemos el punto '.' intacto para logogramas (DUMU.ZI).
        text = text.replace('-', ' ') 

        # PASO 3: Limpieza de caracteres ruidosos (pero conservando puntos)
        # Eliminamos caracteres que no sean letras, números, puntos, espacios o corchetes
        # Nota: Permitimos acentos y caracteres especiales latinos extendidos (š, ṣ, etc)
        text = re.sub(r'[^\w\s\.\[\]ŠšṢṣṬṭÁáÉéÍíÚúÀàÈèÌìÙùÂâÊêÎîÛû]', '', text)

        # PASO 4: Tokenización (Split por espacios)
        tokens = text.split()

        # PASO 5: Post-Procesamiento (Filtrado de vacíos)
        tokens = [t.strip() for t in tokens if t.strip()]

        return tokens

# --- PRUEBA UNITARIA INTEGRADA ---
if __name__ == "__main__":
    tk = KanishTokenizer()
    ejemplos = [
        "um-ma Puzur-Aššur-ma",  # Caso Morfemas
        "DUMU.ZI i-li-ik",       # Caso Logograma (DUMU.ZI debe quedar junto)
        "10 ma-na kù-babbar",    # Caso Numérico
        "kaspum [x] [ ... ]"     # Caso Dañado
    ]
    
    print("--- 🧪 PRUEBA DE REFINERÍA ---")
    for e in ejemplos:
        print(f"In:  {e}")
        print(f"Out: {tk.clean_and_tokenize(e)}")