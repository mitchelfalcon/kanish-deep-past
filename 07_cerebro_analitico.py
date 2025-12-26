import pandas as pd
import networkx as nx
import community.community_louvain as community_louvain # Requiere: pip install python-louvain
from neo4j import GraphDatabase, basic_auth

# --- TUS CREDENCIALES ---
URI = "neo4j://127.0.0.1:7687"
USUARIO = "neo4j"
PASSWORD = "14141010"

class KanishAnalyst:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=basic_auth(USUARIO, PASSWORD))

    def close(self):
        self.driver.close()

    def obtener_grafo_desde_neo4j(self):
        """
        Descarga las relaciones del grafo para analizarlas en memoria con Python.
        """
        print("📥 Descargando topología de la red desde Neo4j...")
        query = """
        MATCH (n:Person)-[r]->(m:Person)
        RETURN n.id AS source, m.id AS target, type(r) AS tipo
        """
        with self.driver.session() as session:
            result = session.run(query)
            df = pd.DataFrame([r.data() for r in result])
        
        if df.empty:
            print("❌ No hay relaciones en el grafo para analizar.")
            return None
            
        # Crear grafo en NetworkX
        G = nx.from_pandas_edgelist(df, 'source', 'target', create_using=nx.Graph())
        print(f"✅ Grafo cargado en memoria: {G.number_of_nodes()} nodos, {G.number_of_edges()} conexiones.")
        return G

    def ejecutar_algoritmos_sna(self, G):
        """
        Aplica matemáticas de grafos para encontrar VIPs y Comunidades.
        """
        print("\n🧠 Ejecutando Algoritmos de Inteligencia Social...")
        
        # 1. Betweenness Centrality (Quién controla el flujo de información/dinero)
        # Nos dice quién es el intermediario clave.
        betweenness = nx.betweenness_centrality(G)
        
        # 2. Algoritmo de Louvain (Detección de Comunidades)
        # Agrupa a las personas en "Familias" o "Clanes" comerciales.
        partition = community_louvain.best_partition(G)
        
        print("   > Centralidad calculada.")
        print(f"   > Comunidades detectadas: {len(set(partition.values()))}")
        
        return betweenness, partition

    def actualizar_neo4j(self, betweenness, partition):
        """
        Escribe los resultados de vuelta en la base de datos.
        """
        print("\n💾 Inyectando inteligencia de vuelta a Neo4j...")
        
        # Preparamos los datos para una carga por lotes (más eficiente)
        datos_actualizacion = []
        for person_id, comunidad_id in partition.items():
            score = betweenness.get(person_id, 0.0)
            datos_actualizacion.append({
                'id': person_id, 
                'community': comunidad_id, 
                'importance': score
            })
            
        query = """
        UNWIND $rows AS row
        MATCH (p:Person {id: row.id})
        SET p.community_louvain = row.community,
            p.centrality_score = row.importance
        """
        
        with self.driver.session() as session:
            session.run(query, rows=datos_actualizacion)
            
        print("✅ Base de datos actualizada con Metadatos Sociales.")

if __name__ == "__main__":
    # Necesitas instalar librerías extra:
    # pip install networkx python-louvain
    
    analista = KanishAnalyst()
    
    # 1. Obtener datos
    Grafo = analista.obtener_grafo_desde_neo4j()
    
    if Grafo:
        # 2. Calcular matemáticas
        scores, comunidades = analista.ejecutar_algoritmos_sna(Grafo)
        
        # 3. Guardar en BD
        analista.actualizar_neo4j(scores, comunidades)
        
        print("\n🎉 Sprint 2 FINALIZADO: El grafo ahora entiende jerarquías y clanes.")
    
    analista.close()