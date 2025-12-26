import os
import random
import re

# --- CONFIGURACIÓN ---
CARPETA_CORPUS = 'output/golden_corpus'
MUESTRAS_A_REVISAR = 5  # Cantidad de archivos aleatorios a auditar

def limpiar_estilo_kaggle(texto_crudo):
    """
    Aplica reglas de limpieza estándar de competiciones NLP (Kaggle).
    Adapta estas reglas según lo que veas en la auditoría.
    """
    texto = str(texto_crudo)
    
    # REGLA 1: Normalización de espacios (Básico en Kaggle)
    # Convierte saltos de línea (\n), tabs (\t) y dobles espacios en un solo espacio.
    texto = re.sub(r'\s+', ' ', texto)
    
    # REGLA 2: Limpieza de artefactos de OCR comunes
    # Elimina cosas como "--- PAGE 3 ---" o números de página sueltos
    texto = re.sub(r'--- PAGE \d+ ---', '', texto)
    texto = re.sub(r'\[Image \d+\]', '', texto) # Elimina marcadores de imagen
    
    # REGLA 3: Eliminar caracteres extraños pero RESPETANDO acentos y transliteraciones
    # En Acadio/Sumerio NECESITAMOS caracteres como š, ṣ, ṭ, así que NO usamos isalnum() estricto.
    # Aquí eliminamos solo caracteres de control no imprimibles si los hubiera.
    texto = "".join(ch for ch in texto if ch.isprintable())
    
    return texto.strip()

def auditar_calidad():
    """
    Selecciona archivos al azar y muestra el ANTES y el DESPUÉS.
    """
    print(f"--- 🕵️ AUDITORÍA DE CALIDAD (ESTÁNDAR KAGGLE) ---")
    
    if not os.path.exists(CARPETA_CORPUS):
        print(f"❌ Error: No existe la carpeta {CARPETA_CORPUS}")
        print("   ¿Ejecutaste primero el script 01_extraer.py?")
        return

    archivos = [f for f in os.listdir(CARPETA_CORPUS) if f.endswith('.txt')]
    
    if not archivos:
        print("❌ La carpeta está vacía.")
        return

    print(f"📚 Total de archivos en el corpus: {len(archivos)}")
    print(f"🎲 Seleccionando {MUESTRAS_A_REVISAR} documentos al azar...\n")
    
    muestras = random.sample(archivos, min(MUESTRAS_A_REVISAR, len(archivos)))

    for nombre_archivo in muestras:
        ruta_completa = os.path.join(CARPETA_CORPUS, nombre_archivo)
        
        with open(ruta_completa, 'r', encoding='utf-8') as f:
            contenido_crudo = f.read()

        # Aplicamos la simulación de limpieza
        contenido_limpio = limpiar_estilo_kaggle(contenido_crudo)
        
        # --- REPORTE VISUAL ---
        print("="*60)
        print(f"📄 ARCHIVO: {nombre_archivo}")
        print(f"📏 Longitud original: {len(contenido_crudo)} caracteres")
        print("-" * 20 + " ORIGINAL (Fragmento) " + "-" * 20)
        print(contenido_crudo[:300] + "...") # Primeros 300 caracteres
        
        print("-" * 20 + " LIMPIEZA KAGGLE " + "-" * 23)
        print(contenido_limpio[:300] + "...") 
        
        # Alerta de símbolos sospechosos (Debugging)
        if "" in contenido_crudo:
            print("\n⚠️ ALERTA: Se detectaron caracteres corruptos () de codificación.")
        if len(contenido_limpio) < 50:
             print("\n⚠️ ALERTA: Este archivo quedó casi vacío tras la limpieza.")
             
        print("="*60 + "\n")

if __name__ == "__main__":
    auditar_calidad()