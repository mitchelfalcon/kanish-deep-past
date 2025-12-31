# src/entity_manager.py
import re

class EntityManager:
    """
    Gestor de Entidades. Normaliza y clasifica entidades antes de ir al Grafo.
    Maneja también la lógica de 'Regex Missing' para entidades rotas.
    """
    def __init__(self):
        # Diccionario de tipos conocidos (Hardcoded o cargado de JSON)
        self.known_types = {
            "Puzur-Aššur": "Person",
            "Enlil": "Deity",
            "Kanesh": "Location",
            "kaspum": "Commodity",
            "KÙ.BABBAR": "Commodity"
        }
        # Regex para detectar entidades rotas dentro de un nombre
        # Ej: "Puzur-[...]"
        self.regex_missing_entity = re.compile(r'\[x+\]|\[\.+\]|<BROKEN>')

    def classify_entity(self, token):
        """Asigna una etiqueta ontológica a un token"""
        
        # 1. Chequeo de Integridad (Regex Missing)
        if self.regex_missing_entity.search(token):
            return "BrokenEntity"
            
        # 2. Búsqueda en Diccionario
        # Normalizamos quitando acentos o mayúsculas si es necesario
        clean_token = token.replace('.', ' ').strip()
        # Lógica simple de búsqueda
        for key, type_ in self.known_types.items():
            if key in clean_token:
                return type_
                
        # 3. Fallback (Desconocido)
        return "Unknown"

    def extract_entities_from_text(self, text):
        """
        Simulación de extracción. En producción, aquí llamas a GLiNER.
        """
        tokens = text.split()
        entities = []
        for t in tokens:
            # Si empieza con mayúscula, es candidato a entidad
            if t[0].isupper():
                etype = self.classify_entity(t)
                entities.append({"text": t, "type": etype})
        return entities