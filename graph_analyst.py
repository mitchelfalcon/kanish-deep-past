import pandas as pd
import networkx as nx
import community.community_louvain as community_louvain # Requiere: pip install python-louvain
import os
import re
import sys

# Ajuste de rutas para importar configuración
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from src.config import PATHS
except ImportError:
    # Fallback si no existe config.py aún
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PATHS = {
        "OUTPUT_CLEAN": os.path.join(BASE_DIR, "input", "processed", "preprocessing.csv"),
        "SOCIAL_METRICS": os.path.join(BASE_DIR, "input", "processed", "social_metrics.csv")
    }

class SocialGraphEngine:
    """
    Motor de Análisis de Redes Sociales (SNA).
    Convierte texto en grafos matemáticos para entender la estructura de Kanesh.
    """
    def __init__(self):
        self.G = nx.Graph()
        # Regex simple para detectar posibles Nombres Propios (Mayúscula inicial)
        # En producción, esto se reemplaza por el output de GLiNER.
        self.name_pattern = re.compile(r'\b[A-Z][a-z]+\b')
        
        # Lista negra de palabras comunes que parecen nombres pero no lo son
        self.stoplist = {"The", "And", "To", "From", "Silver", "Gold", "Tablet", "Mina", "Shekel", "City"}

    def _extract_entities_heuristic(self, text):
        """
        Extracción rápida de entidades basada en mayúsculas (Heurística).
        Sirve para generar el grafo inicial sin depender del modelo pesado NER.
        """
        if not isinstance(text, str): return []
        
        candidates = self.name_pattern.findall(text)
        # Filtrar palabras comunes y duplicados
        unique_names = list(set([c for c in candidates if c not in self.stoplist and len(c) > 2]))
        return unique_names

    def build_graph(self, csv_path):
        print(f"🕸️  Construyendo Grafo Social desde: {csv_path}...")
        
        if not os.path.exists(csv_path):
            print(f"❌ Error: No existe {csv_path}. Ejecuta primero preprocessing.py")
            return

        df = pd.read_csv(csv_path)
        
        # Asumimos columna 'clean_text' o 'transliteration'
        col_text = 'clean_text' if 'clean_text' in df.columns else 'transliteration'
        if col_text not in df.columns:
            # Intento final
            col_text = df.columns[1] 

        transaction_count = 0
        
        for _, row in df.iterrows():
            text = str(row[col_text])
            entities = self._extract_entities_heuristic(text)
            
            if len(entities) > 1:
                transaction_count += 1
                # Crear enlaces (clique) entre todos los mencionados en la tablilla
                # Si Puzur, Enlil y Amur están en el texto, se conocen entre sí.
                for i in range(len(entities)):
                    for j in range(i + 1, len(entities)):
                        # Añadimos peso (weight) si ya existe la relación
                        if self.G.has_edge(entities[i], entities[j]):
                            self.G[entities[i]][entities[j]]['weight'] += 1
                        else:
                            self.G.add_edge(entities[i], entities[j], weight=1)

        print(f"   > Transacciones procesadas: {transaction_count}")
        print(f"   > Nodos (Personas): {self.G.number_of_nodes()}")
        print(f"   > Aristas (Relaciones): {self.G.number_of_edges()}")

    def analyze_and_save(self, output_path):
        if len(self.G.nodes) == 0:
            print("⚠️ El grafo está vacío. Revisa la extracción de entidades.")
            return

        print("🧠 Ejecutando Algoritmos de Grafos (SNA)...")
        
        # 1. Betweenness Centrality (¿Quién controla el flujo?)
        # Esto nos dice quiénes son los mercaderes más importantes.
        print("   > Calculando Centralidad...")
        centrality = nx.betweenness_centrality(self.G)
        
        # 2. Louvain Community Detection (¿A qué familia pertenecen?)
        # Agrupa los nodos en clanes comerciales.
        print("   > Detectando Comunidades (Louvain)...")
        try:
            partition = community_louvain.best_partition(self.G)
        except:
            print("   ⚠️ Error en Louvain (quizás grafo muy pequeño). Asignando comunidad 0.")
            partition = {node: 0 for node in self.G.nodes}

        # 3. Grado (Cuántos contactos directos tiene)
        degree = dict(self.G.degree())

        # Consolidar resultados
        data = []
        for node in self.G.nodes:
            data.append({
                'entity': node,
                'centrality_score': centrality.get(node, 0),
                'community_id': partition.get(node, 0),
                'degree_connections': degree.get(node, 0)
            })
            
        # Guardar CSV
        df_metrics = pd.DataFrame(data)
        
        # Ordenar por importancia
        df_metrics = df_metrics.sort_values(by='centrality_score', ascending=False)
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        df_metrics.to_csv(output_path, index=False)
        print(f"✅ Métricas Sociales guardadas en: {output_path}")
        print(f"   Top 3 'Padrinos' de Kanesh:\n{df_metrics.head(3)}")

if __name__ == "__main__":
    # Definir ruta de salida si no viene de config
    out_path = PATHS.get("SOCIAL_METRICS", "input/processed/social_metrics.csv")
    in_path = PATHS.get("OUTPUT_CLEAN", "input/processed/preprocessing.csv")
    
    engine = SocialGraphEngine()
    engine.build_graph(in_path)
    engine.analyze_and_save(out_path)