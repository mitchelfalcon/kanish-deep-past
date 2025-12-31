import csv
import logging
from typing import Dict, List, Optional

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GematriaRegistry:
    """
    Gestiona la asignación de valores primos a raíces y signos.
    Actúa como la fuente de verdad (Truth Source) y base de datos en memoria.
    """
    
    def __init__(self, lexicon_path: str = None):
        self.sign_map: Dict[str, int] = {}
        self.prime_cursor = 2  # Primer número primo
        self.collision_log: List[str] = []
        
        # Carga inicial (Mock o Real si se provee path)
        if lexicon_path:
            self.load_lexicon(lexicon_path)
        else:
            self._initialize_mock_data()

    def _is_prime(self, n: int) -> bool:
        """Helper básico para verificar primos."""
        if n <= 1: return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    def _get_next_prime(self) -> int:
        """Obtiene el siguiente número primo disponible."""
        while True:
            if self._is_prime(self.prime_cursor):
                val = self.prime_cursor
                self.prime_cursor += 1
                return val
            self.prime_cursor += 1

    def _initialize_mock_data(self):
        """Datos semilla para pruebas unitarias sin el CSV completo."""
        logging.info("Inicializando registro con datos semilla (MOCK)...")
        # Ejemplo: Asignando primos arbitrarios a signos conocidos
        mock_data = ["É", "GAL", "DUMU", "MUNUS", "be", "lí", "ni"]
        for token in mock_data:
            self.register_token(token)

    def load_lexicon(self, filepath: str):
        """
        Carga OA_Lexicon_eBL.csv.
        Estructura esperada CSV: sign, reading, interpretation
        """
        try:
            with open(filepath, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Asumimos columna 'sign' o 'reading' como clave
                    key = row.get('reading', row.get('sign'))
                    if key:
                        self.register_token(key)
            logging.info(f"Lexicon cargado. Total entradas: {len(self.sign_map)}")
        except FileNotFoundError:
            logging.error(f"No se encontró el archivo de léxico: {filepath}")

    def register_token(self, token: str) -> int:
        """Asigna un valor primo único a un token si no existe."""
        if token not in self.sign_map:
            prime = self._get_next_prime()
            self.sign_map[token] = prime
        return self.sign_map[token]

    def get_gematria_value(self, token: str) -> int:
        """
        Retorna el valor primo del token.
        Retorna 0 para tokens neutros ([DMG], [UNK]).
        """
        if token in ["[DMG]", "[MISSING]", "[UNK]", "x"]:
            return 0
        return self.sign_map.get(token, 0)

    def calculate_hash(self, token_list: List[str]) -> int:
        """
        Cálculo Vectorial: Suma de valores primos para obtener el Gematria_Hash de una frase/segmento.
        """
        vector_sum = 0
        for token in token_list:
            val = self.get_gematria_value(token)
            if val == 0 and token not in ["[DMG]", "[MISSING]", "x"]:
                logging.warning(f"Token desconocido encontrado en cálculo: {token}")
            vector_sum += val
        return vector_sum