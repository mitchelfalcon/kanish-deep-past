import re

class KanishTokenizer:
    """
    Tokenizador especializado para textos cuneiformes (Old Assyrian).
    Separa morfemas gramaticales (-ma, -ni) sin romper logogramas.
    """
    
    def __init__(self):
        # Lista de clíticos comunes en Kanesh para separar
        # -ma: Enfático / Conectivo
        # -ni: Subjuntivo
        # -kum/šum: Dativo
        # -am: Ventivo
        self.cliticos = [
            'ma', 'ni', 'kum', 'šum', 'am', 'kunu', 'šunu', 'ka', 'su'
        ]
        
        # Regex compilado para velocidad
        # Busca un guion seguido de un clítico, pero SOLO si es el final de la palabra (\b)
        self.regex_cliticos = re.compile(r'-(' + '|'.join(self.cliticos) + r')\b', re.IGNORECASE)

    def tokenizar(self, texto):
        if not texto or not isinstance(texto, str):
            return []

        texto = texto.strip()

        # PASO 1: Protección de Logogramas complejos (Heurística)
        # Si hay puntos (DUMU.ZI) asumimos que es un logograma y no lo tocamos por ahora.
        # (En versiones futuras, esto se conecta al Grafo para validar entidades)

        # PASO 2: Separación Quirúrgica de Clíticos
        # Transforma "iqbi-ma" en "iqbi -ma"
        texto_procesado = self.regex_cliticos.sub(r' -\1', texto)
        
        # PASO 3: Split estándar por espacios
        tokens = texto_procesado.split()
        
        return tokens

# --- BLOQUE DE PRUEBA RÁPIDA ---
if __name__ == "__main__":
    tk = KanishTokenizer()
    ejemplos = [
        "um-ma En-lil-ba-ni-ma",       # Nombre propio + clítico -ma
        "kù-babbar i-di-in-šum",       # Verbo + clítico dativo -šum
        "DUMU.ZI i-li-ik",             # Logograma con punto (no debe separarse)
        "a-na bīt kar-im",             # Preposición y sustantivo
        "[x ... ] <BROKEN>"            # Token de rotura (del paso anterior)
    ]
    
    print("--- 🧪 PRUEBA DE TOKENIZACIÓN ---")
    for ej in ejemplos:
        print(f"ORIGINAL: {ej}")
        print(f"TOKENS:   {tk.tokenizar(ej)}")
        print("-" * 30)