import pandas as pd
import logging
import os

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CorpusIngestor:
    """
    Maneja la carga de datasets (Tabla A, train/test) y la validación UTF-8.
    Responsable de reportar estadísticas de integridad de datos.
    """

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.train_df = None
        self.test_df = None
        self.unknown_signs_log = "unknown_signs.log"

    def load_corpus(self, train_file: str = "train.csv", test_file: str = "test.csv"):
        """
        Carga los CSVs principales.
        """
        train_path = os.path.join(self.data_dir, train_file)
        test_path = os.path.join(self.data_dir, test_file)

        if os.path.exists(train_path):
            try:
                self.train_df = pd.read_csv(train_path, encoding='utf-8')
                logging.info(f"Train set cargado: {len(self.train_df)} registros.")
            except Exception as e:
                logging.error(f"Error cargando train set: {e}")
        else:
            logging.warning(f"Archivo train no encontrado en {train_path}")

        if os.path.exists(test_path):
            try:
                self.test_df = pd.read_csv(test_path, encoding='utf-8')
                logging.info(f"Test set cargado: {len(self.test_df)} registros.")
            except Exception as e:
                logging.error(f"Error cargando test set: {e}")

    def report_stats(self):
        """
        Genera estadísticas sobre signos dañados y calidad del corpus.
        """
        if self.train_df is None:
            logging.warning("No hay datos cargados para reportar.")
            return

        # Asumiendo columna 'cuneiform' o 'transliteration'
        target_col = 'transliteration' if 'transliteration' in self.train_df.columns else self.train_df.columns[0]
        
        total_rows = len(self.train_df)
        damaged_rows = self.train_df[target_col].str.contains('x|\[...\]', regex=True).sum()
        
        print("\n--- CORPUS HEALTH REPORT ---")
        print(f"Total Rows: {total_rows}")
        print(f"Damaged/Lacunae Detected: {damaged_rows}")
        print(f"Integrity Ratio: {((total_rows - damaged_rows)/total_rows)*100:.2f}%")
        print("----------------------------\n")

    def log_unknown_sign(self, sign_id: str, source_ref: str):
        """
        Registra signos no encontrados en el índice para revisión humana.
        """
        with open(self.unknown_signs_log, "a", encoding="utf-8") as f:
            f.write(f"UNKNOWN: {sign_id} detected in {source_ref}\n")