# src/ontology_injector.py
from neo4j import GraphDatabase

class OntologyInjector:
    """
    Encargado del 'Schema Design' y la carga de grafos.
    Define la estructura rígida de la realidad de Kanesh.
    """
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)

    def apply_schema_design(self):
        """
        Ejecuta las restricciones ontológicas (Schema).
        Esto asegura que no haya datos duplicados o tipos incorrectos.
        """
        queries = [
            # Entidades Únicas
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Commodity) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE",
            
            # Índices para búsqueda rápida (Semantic Hashing lookup)
            "CREATE INDEX IF NOT EXISTS FOR (t:Tablet) ON (t.semantic_hash)"
        ]
        
        print("💉 Inyectando Diseño de Esquema (Schema Design)...")
        with self.driver.session() as session:
            for q in queries:
                session.run(q)
        print("✅ Esquema Ontológico aplicado.")

    def inject_triplet(self, subject, predicate, object_, tablet_id):
        """
        Inyecta una relación: (Sujeto)-[PREDICADO]->(Objeto)
        Ej: (Puzur-Ashur)-[OWES]->(Silver)
        """
        query = """
        MERGE (s:Person {name: $sub})
        MERGE (o:Commodity {name: $obj})
        MERGE (t:Tablet {id: $tid})
        
        # Relación dinámica según el predicado
        MERGE (s)-[r:TRANSACTION {type: $pred}]->(o)
        SET r.source = $tid
        """
        # Nota: En producción, esto se expande para manejar Locations, Roles, etc.
        with self.driver.session() as session:
            session.run(query, sub=subject, obj=object_, pred=predicate, tid=tablet_id)