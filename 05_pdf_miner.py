import pdfplumber
import pandas as pd
import os
import re

# --- CONFIGURACIÓN ---
CARPETA_PDFS = 'input/pdfs_bibliografia'  # PON AQUÍ TUS 900 PDFs
CARPETA_SALIDA = 'output/dataset_aumentado'

class PDFMinerKanish:
    def __init__(self):
        self.datos_extraidos = []
        # Patrones para detectar dónde empieza una traducción en papers académicos
        self.patron_translit = re.compile(r'^\d{1,3}\.\s.*') # Ej: "1. um-ma Puzur-Aššur"
        self.patron_traduccion = re.compile(r'^(Translat|Meaning|Note):', re.IGNORECASE)

    def extraer_texto_pdf(self, ruta_pdf):
        pares_encontrados = []
        buffer_translit = []
        buffer_trad = []
        capturando_translit = False
        capturando_trad = False

        try:
            with pdfplumber.open(ruta_pdf) as pdf:
                for pagina in pdf.pages:
                    texto = pagina.extract_text()
                    if not texto: continue
                    
                    lineas = texto.split('\n')
                    for linea in lineas:
                        linea = linea.strip()
                        if len(linea) < 5: continue

                        # 1. Detectar Transliteración (Líneas numeradas con palabras acadias)
                        if self.patron_translit.match(linea) and ('-' in linea or 'um-ma' in linea):
                            if capturando_trad and buffer_translit:
                                # Guardar par anterior si existía
                                pares_encontrados.append({
                                    'transliteracion': " ".join(buffer_translit),
                                    'traduccion': " ".join(buffer_trad)
                                })
                                buffer_translit = []
                                buffer_trad = []
                            
                            capturando_translit = True
                            capturando_trad = False
                            buffer_translit.append(linea)

                        # 2. Detectar Traducción
                        elif self.patron_traduccion.match(linea):
                            capturando_translit = False
                            capturando_trad = True
                        
                        # 3. Acumular líneas
                        elif capturando_translit:
                            buffer_translit.append(linea)
                        elif capturando_trad:
                            buffer_trad.append(linea)

        except Exception as e:
            print(f"⚠️ Error leyendo {os.path.basename(ruta_pdf)}: {e}")
        
        return pares_encontrados

    def ejecutar_mineria(self):
        print(f"--- ⛏️ INICIANDO MINERÍA EN {CARPETA_PDFS} ---")
        
        if not os.path.exists(CARPETA_PDFS):
            os.makedirs(CARPETA_PDFS)
            print(f"❌ La carpeta {CARPETA_PDFS} no existe. Créala y añade los PDFs.")
            return

        archivos = [f for f in os.listdir(CARPETA_PDFS) if f.endswith('.pdf')]
        print(f"📚 PDFs encontrados: {len(archivos)}")

        total_pares = 0
        for archivo in archivos:
            ruta = os.path.join(CARPETA_PDFS, archivo)
            print(f"   > Procesando: {archivo}...")
            
            nuevos_pares = self.extraer_texto_pdf(ruta)
            
            if nuevos_pares:
                for p in nuevos_pares:
                    p['archivo_origen'] = archivo
                self.datos_extraidos.extend(nuevos_pares)
                print(f"     ✨ {len(nuevos_pares)} pares extraídos.")
                total_pares += len(nuevos_pares)

        # Guardar resultados
        if self.datos_extraidos:
            if not os.path.exists(CARPETA_SALIDA):
                os.makedirs(CARPETA_SALIDA)
            
            df = pd.DataFrame(self.datos_extraidos)
            ruta_csv = os.path.join(CARPETA_SALIDA, 'corpus_aumentado.csv')
            df.to_csv(ruta_csv, index=False)
            print(f"\n✅ MINERÍA COMPLETADA. {total_pares} pares guardados en: {ruta_csv}")
        else:
            print("\n⚠️ No se extrajeron datos. Revisa si los PDFs tienen texto seleccionable (no imagen).")

if __name__ == "__main__":
    miner = PDFMinerKanish()
    miner.ejecutar_mineria()