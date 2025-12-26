import pandas as pd
import re
import os
import zipfile
import sys

# --- CONFIGURACIÓN ESPECÍFICA PARA TU ENTORNO ---
# El archivo exacto que tienes en tu lista
ZIP_ARCHIVO = 'deep-past-initiative-machine-translation.zip'

# El archivo que buscamos DENTRO del zip (puede variar ligeramente de nombre)
CSV_OBJETIVO = 'publications.csv' 

# Donde guardaremos los resultados limpios
CARPETA_SALIDA = 'output/golden_corpus'

def buscar_y_extraer():
    """
    Función inteligente que ignora PDFs de libros y diccionarios,
    y va directo al ZIP de la competencia.
    """
    print(f"--- 🕵️ INICIANDO ESCANEO INTELIGENTE ---")
    
    # 1. BUSCAR EL ZIP
    # Buscamos en la carpeta actual donde ejecutas el script
    if not os.path.exists(ZIP_ARCHIVO):
        # Intento de búsqueda en subcarpetas por si acaso
        encontrado = False
        for root, dirs, files in os.walk('.'):
            if ZIP_ARCHIVO in files:
                ruta_zip = os.path.join(root, ZIP_ARCHIVO)
                print(f"✅ Archivo ZIP encontrado en: {ruta_zip}")
                encontrado = True
                break
        
        if not encontrado:
            print(f"❌ ERROR: No encuentro '{ZIP_ARCHIVO}'.")
            print("Asegúrate de ejecutar este script en la misma carpeta donde descargaste los archivos.")
            return None
    else:
        ruta_zip = ZIP_ARCHIVO
        print(f"✅ Archivo ZIP detectado: {ruta_zip}")

    # 2. LEER EL ZIP SIN DESCOMPRIMIR TODO (Ahorra espacio)
    print("📦 Inspeccionando contenido del ZIP...")
    try:
        with zipfile.ZipFile(ruta_zip, 'r') as z:
            # Listar archivos dentro del zip
            nombres_zip = z.namelist()
            
            # Buscar el CSV de publicaciones (a veces está en una subcarpeta dentro del zip)
            candidatos = [f for f in nombres_zip if 'publications' in f and f.endswith('.csv')]
            
            if not candidatos:
                print("❌ No encontré 'publications.csv' dentro del ZIP.")
                return None
            
            archivo_a_extraer = candidatos[0] # Tomamos el primero que coincida
            print(f"📖 Extrayendo: {archivo_a_extraer}...")
            
            # Extraemos SOLO ese archivo a una carpeta temporal
            z.extract(archivo_a_extraer, 'temp_data')
            ruta_csv = os.path.join('temp_data', archivo_a_extraer)
            
            return ruta_csv
            
    except zipfile.BadZipFile:
        print("❌ El archivo ZIP parece estar corrupto.")
        return None

def procesar_datos(ruta_csv):
    if not ruta_csv: return

    print(f"📊 Leyendo base de datos...")
    try:
        df = pd.read_csv(ruta_csv)
    except Exception as e:
        print(f"Error leyendo CSV: {e}")
        return

    # 3. FILTRADO QUIRÚRGICO (MICHEL / LARSEN / VEENHOF)
    # Ignoramos tus libros de Python y CADs, nos centramos en los expertos en Acadio.
    keywords = [
        r'Cécile.*Michel', 
        r'Mogens.*Larsen', 
        r'K\.R\..*Veenhof', 
        r'AKT', 
        r'OAA'
    ]
    patron = "|".join(keywords)
    
    print("🔍 Filtrando textos de alta calidad...")
    
    # Detectar columna correcta
    col_nombre = 'pdf_name' if 'pdf_name' in df.columns else 'title'
    
    # Filtrar
    df_golden = df[df[col_nombre].str.contains(patron, case=False, regex=True, na=False)]
    
    print(f"   > Total documentos en CSV: {len(df)}")
    print(f"   > Documentos 'Golden' encontrados: {len(df_golden)}")
    
    # 4. GUARDAR RESULTADOS
    if not os.path.exists(CARPETA_SALIDA):
        os.makedirs(CARPETA_SALIDA)
    
    count = 0
    print(f"💾 Guardando archivos limpios en '{CARPETA_SALIDA}'...")
    
    for index, row in df_golden.iterrows():
        # Limpieza de nombre
        nombre_crudo = str(row.get(col_nombre, f'doc_{index}'))
        nombre_seguro = re.sub(r'[^\w\-_\.]', '_', nombre_crudo)
        
        # Obtener texto (probamos varias columnas posibles)
        contenido = row.get('page_text', row.get('text', ''))
        
        if pd.isna(contenido) or len(str(contenido)) < 100:
            continue
            
        with open(f"{CARPETA_SALIDA}/{nombre_seguro}.txt", "w", encoding="utf-8") as f:
            f.write(str(contenido))
        count += 1

    print(f"\n🎉 ¡PROCESO COMPLETADO!")
    print(f"✅ Se han ignorado tus libros de Python y diccionarios CAD.")
    print(f"✅ Se han generado {count} archivos de texto listos para minar en: {CARPETA_SALIDA}")

    # Limpieza (Opcional: borrar carpeta temporal)
    # import shutil
    # shutil.rmtree('temp_data')

if __name__ == "__main__":
    archivo_csv = buscar_y_extraer()
    procesar_datos(archivo_csv)