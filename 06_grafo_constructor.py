import pandas as pd
from neo4j import GraphDatabase, basic_auth
import sys

# --- CONFIGURACIÓN DE CONEXIÓN (YA ACTUALIZADA) ---
# He puesto aquí tus datos exactos:
URI = "neo4j://127.0.0.1:7687" 
USUARIO = "neo4j"
PASSWORD = "14141010" 

class KanishGraphBuilder:
    """
    Arquitecto del Grafo de Conocimiento de Kanish.
    Define el esquema (Ontología) e ingesta entidades y relaciones.
    """
    def __init__(self):
        try:
            # Conectamos usando tus credenciales
            self.driver = GraphDatabase.driver(URI, auth=basic_auth(USUARIO, PASSWORD))
            self.driver.verify_connectivity()
            print(f"✅ Conectado exitosamente a Neo4j en {URI}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            print("   Verifica que Neo4j Desktop esté abierto y la base de datos con 'Start'.")
            sys.exit(1)

    def close(self):
        self.driver.close()

    def definir_ontologia(self):
        """
        Crea las restricciones de unicidad. Esto evita duplicados.
        Equivalente a las 'Primary Keys' en SQL.
        """
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Commodity) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Text) REQUIRE t.id IS UNIQUE"
        ]
        
        print("🏗️  Construyendo esquema y restricciones...")
        with self.driver.session() as session:
            for q in queries:
                session.run(q)
        print("   > Restricciones aplicadas (Personas, Mercancías, Textos).")

    def ingestar_personas(self, df):
        """
        Crea nodos de Personas. Usa MERGE para no duplicar si ejecutas el script 2 veces.
        """
        query = """
        UNWIND $rows AS row
        MERGE (p:Person {id: row.id})
        ON CREATE SET p.name = row.name, p.role = row.role, p.origin = row.origin
        RETURN count(p) as total
        """
        with self.driver.session() as session:
            res = session.run(query, rows=df.to_dict('records'))
            print(f"👥 Personas procesadas: {res.single()['total']}")

    def tejer_relaciones_familiares(self, df):
        """
        Crea la red genealógica: (Hijo)-[:SON_OF]->(Padre)
        Clave para desambiguar homónimos.
        """
        query = """
        UNWIND $rows AS row
        MATCH (hijo:Person {id: row.child_id})
        MATCH (padre:Person {id: row.father_id})
        MERGE (hijo)-[:SON_OF]->(padre)
        """
        with self.driver.session() as session:
            session.run(query, rows=df.to_dict('records'))
            print(f"🔗 Lazos familiares creados: {len(df)}")

    def registrar_deudas(self, df):
        """
        Crea la red económica: (Deudor)-[:OWES]->(Acreedor)
        """
        query = """
        UNWIND $rows AS row
        MATCH (d:Person {id: row.debtor_id})
        MATCH (c:Person {id: row.creditor_id})
        MERGE (d)-[r:OWES]->(c)
        SET r.amount = row.amount, 
            r.commodity = row.commodity,
            r.text_source = row.text_id
        """
        with self.driver.session() as session:
            session.run(query, rows=df.to_dict('records'))
            print(f"💰 Deudas registradas: {len(df)}")

# --- SIMULACIÓN DE DATOS (SEMILLA) ---
# Esto creará unos pocos datos de prueba para verificar que el Grafo funciona.
def generar_datos_semilla():
    # 1. Personas Clave de Kanesh
    personas = pd.DataFrame([
        {'id': 'p1', 'name': 'Puzur-Aššur', 'role': 'Merchant', 'origin': 'Assur'},
        {'id': 'p2', 'name': 'Ištar-lamassi', 'role': 'Matriarch', 'origin': 'Kanesh'},
        {'id': 'p3', 'name': 'Enlil-bani', 'role': 'Scribe', 'origin': 'Assur'},
        {'id': 'p4', 'name': 'Amur-Ištar', 'role': 'Merchant', 'origin': 'Assur'}
    ])
    
    # 2. Genealogía (Puzur-Aššur es hijo de Ištar-lamassi en esta ficción)
    familia = pd.DataFrame([
        {'child_id': 'p1', 'father_id': 'p2'}, 
        {'child_id': 'p4', 'father_id': 'p3'}
    ])
    
    # 3. Economía (Quién debe a quién)
    deudas = pd.DataFrame([
        {'debtor_id': 'p1', 'creditor_id': 'p3', 'amount': 5.5, 'commodity': 'Silver', 'text_id': 'kt_94_k_823'},
        {'debtor_id': 'p4', 'creditor_id': 'p1', 'amount': 120, 'commodity': 'Textiles', 'text_id': 'kt_91_k_100'}
    ])
    
    return personas, familia, deudas

if __name__ == "__main__":
    print("--- 🚀 INICIANDO CONSTRUCCIÓN DEL GRAFO KANISH ---")
    
    # Instanciamos el constructor (ya tiene tu contraseña dentro)
    builder = KanishGraphBuilder()
    
    # Generar datos simulados
    print("🎲 Generando datos semilla...")
    df_p, df_f, df_d = generar_datos_semilla()
    
    # Ejecutar la construcción en Neo4j
    builder.definir_ontologia()
    builder.ingestar_personas(df_p)
    builder.tejer_relaciones_familiares(df_f)
    builder.registrar_deudas(df_d)
    
    builder.close()
    print("\n✨ ¡PROCESO COMPLETADO!")
    print("   El 'Cerebro' (Grafo) ha sido inicializado con éxito.")
    print("   Ahora ve a Neo4j Desktop para ver los nodos.")