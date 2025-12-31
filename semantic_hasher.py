# src/semantic_hasher.py
import json
from functools import reduce

class SemanticHasher:
    """
    Implementación del 'Prime Cipher' (SDIC-G).
    Convierte texto en un Hash Semántico único usando multiplicación de primos.
    Esto permite comparar tablillas matemáticamente, no lingüísticamente.
    """
    def __init__(self, cipher_path="config/master_cipher.json"):
        try:
            with open(cipher_path, 'r') as f:
                self.cipher = json.load(f).get('registry', {})
        except FileNotFoundError:
            self.cipher = {}
            # Fallback (Valores por defecto si no hay JSON)
            self._default_primes = {"KÙ.BABBAR": 2, "AN.NA": 3, "TÚG": 5, "DUMU": 7}

    def _get_prime(self, token):
        # Si está en el registro, devuelve su primo. Si no, devuelve 1 (neutro).
        # En una versión avanzada, asignaría primos dinámicos a desconocidos.
        token_upper = token.upper()
        if token_upper in self.cipher:
            entry = self.cipher[token_upper]
            # Manejar si el registro es una lista o dict
            return entry.get('prime', 1) if isinstance(entry, dict) else 1
        return self._default_primes.get(token_upper, 1)

    def compute_hash(self, text_tokens):
        """
        Calcula el vector semántico: V(frase) = Π (primos de tokens)
        Ej: "Plata y Oro" -> 2 * 1 * 11 = 22
        """
        primes = [self._get_prime(t) for t in text_tokens]
        # Multiplicación acumulativa (Productoria)
        semantic_hash = reduce(lambda x, y: x * y, primes, 1)
        return semantic_hash

    def compare_similarity(self, hash_a, hash_b):
        """
        Si Hash A es divisible por Hash B, entonces la frase B está contenida en A.
        Esto es magia matemática pura.
        """
        if hash_b == 0: return False
        return (hash_a % hash_b) == 0