import sys
import json
# Importamos nuestros módulos locales
from src.data_loader import DataLoader
from src.cape_parser import CapeParser
from src.reconstructor import SyntacticReconstructor

# --- CONFIGURACIÓN ---
CIPHER_PATH = "config/master_cipher.json"

def run_sdic_g_system():
    print("--- 🏛️ SDIC-G SYSTEM SPEC v7.1 [SCIENTIFIC] ---")
    print("Estado: Deterministic Translation Engine Initialized.\n")

    # 1. Cargar Cimientos (Sprint 1)
    try:
        loader = DataLoader(CIPHER_PATH)
    except FileNotFoundError:
        print(f"❌ Error: No se encuentra {CIPHER_PATH}. Ejecuta el Sprint 1.")
        return

    # 2. Inicializar Motores (Sprint 2 & 3)
    parser = CapeParser(loader.cipher)
    compiler = SyntacticReconstructor()

    # --- SIMULACIÓN DE DATOS DE ENTRADA (Como si vinieran del CSV) ---
    # Caso 1: Polivalencia UD (Precedido por KÙ -> Debe ser 'white/pure')
    # Caso 2: Polivalencia UD (Precedido por Número -> Debe ser 'day')
    test_cases = [
        ["DAM.GÀR", "KÙ", "UD", "ANA", "Enlil"],
        ["5", "UD", "DUB", "É.GAL"],
        ["DAM.GÀR", "[...]", "UNK_SIGN"]
    ]

    print("--- 🔬 PROCESSING BATCH ---")
    
    for idx, raw_tokens in enumerate(test_cases):
        print(f"\n>>> CASE {idx+1}: {raw_tokens}")
        
        # FASE 2: Parsing Determinista
        parsed_vector = parser.parse_sequence(raw_tokens)
        
        # Debugging del Vector (Trazabilidad Matemática)
        print(f"    [Trace]: {[t.get('english', 'ERR') for t in parsed_vector]}")

        # FASE 3: Reconstrucción Sintáctica
        translation = compiler.reconstruct(parsed_vector)
        
        print(f"    [OUTPUT]: {translation}")

if __name__ == "__main__":
    run_sdic_g_system()