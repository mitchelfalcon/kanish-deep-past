import os
import re
import time

# --- CONFIGURACIÓN ---
CARPETA_ENTRADA = 'output/golden_corpus'
CARPETA_SALIDA = 'output/kaggle_ready'  # Nombre más específico
ARCHIVO_LOG = 'reporte_anomalias_kaggle.txt'

def limpiar_reglas_kanish(texto_crudo):
    """
    Aplica las reglas del SPRINT 1 del Proyecto Kanish.
    Objetivo: Normalización estricta para NMT (Neural Machine Translation).
    """
    texto = str(texto_crudo)
    
    # 1. ELIMINACIÓN DE RUIDO OCR (Encabezados y pies de página)
    # Borra "--- PAGE 12 ---", "[Image 4]", etc.
    texto = re.sub(r'--- PAGE \d+ ---', '', texto)
    texto = re.sub(r'\[Image \d+\]', '', texto)

    # 2. ESTANDARIZACIÓN DE SIGNOS DAÑADOS (Regla Crítica Kanish)
    # Convierte [...], [x], [x x], [..] en el token único <BROKEN>
    # Explicación Regex: \[ (corchete abirto) seguido de x, puntos o espacios, seguido de \] (cerrado)
    texto = re.sub(r'\[[x\.\s]+\]', ' <BROKEN> ', texto)
    
    # 3. NORMALIZACIÓN DE CARACTERES UNICODE
    # En Acadio, a veces 'š' viene mal codificado. Aquí aseguramos imprimibles.
    texto = "".join(ch for ch in texto if ch.isprintable())

    # 4. LIMPIEZA DE ESPACIOS
    # Colapsar múltiples espacios/tabs/newlines en uno solo
    texto = re.sub(r'\s+', ' ', texto)
    
    # 5. PRE-TOKENIZACIÓN DE CLÍTICOS (Opcional pero recomendado en tu Hoja de Ruta)
    # Separa sufijos comunes (-ma, -ni) para que la IA los entienda mejor.
    # Ej: "iqbi-ma" -> "iqbi -ma"
    texto = re.sub(r'-(ma|ni|ku|šu|ka)\b', r' -\1', texto)

    return texto.strip()

def procesar_corpus_kaggle():
    print(f"--- 🏆 INICIANDO PROTOCOLO DE LIMPIEZA KAGGLE ---")
    
    if not os.path.exists(CARPETA_SALIDA):
        os.makedirs(CARPETA_SALIDA)
        print(f"📁 Carpeta destino: {CARPETA_SALIDA}")
    
    archivos = [f for f in os.listdir(CARPETA_ENTRADA) if f.endswith('.txt')]
    total = len(archivos)
    
    print(f"📚 Archivos a normalizar: {total}")
    print("⚙️  Aplicando tokens <BROKEN> y separando clíticos...")

    validos = 0
    descartados = 0
    
    with open(ARCHIVO_LOG, 'w', encoding='utf-8') as log:
        log.write("REPORTE DE LIMPIEZA (ESTÁNDAR KANISH)\n")
        
        for i, nombre in enumerate(archivos):
            ruta_in = os.path.join(CARPETA_ENTRADA, nombre)
            ruta_out = os.path.join(CARPETA_SALIDA, nombre)
            
            try:
                with open(ruta_in, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # APLICAR REGLAS
                texto_limpio = limpiar_reglas_kanish(contenido)
                
                # FILTRO DE CALIDAD (Mínimo 20 caracteres útiles)
                if len(texto_limpio) < 20:
                    descartados += 1
                    log.write(f"[DESCARTADO] {nombre} - Muy corto/Vacío tras limpieza\n")
                else:
                    with open(ruta_out, 'w', encoding='utf-8') as f_out:
                        f_out.write(texto_limpio)
                    validos += 1
                    
            except Exception as e:
                log.write(f"[ERROR] {nombre}: {e}\n")

            # Progreso
            if (i+1) % 2000 == 0:
                print(f"   ... Procesados {i+1}/{total} ({(i+1)/total:.0%})")

    print(f"\n✅ ¡MISIÓN CUMPLIDA!")
    print(f"   > Archivos Listos para Entrenamiento: {validos}")
    print(f"   > Archivos Descartados: {descartados}")
    print(f"   > Ubicación: {CARPETA_SALIDA}")
    print(f"   > Token especial <BROKEN> insertado correctamente.")

if __name__ == "__main__":
    procesar_corpus_kaggle()