from neo4j import GraphDatabase

URI = "bolt://127.0.0.1:7687"
AUTH = ("neo4j", "lintang123") 

driver = GraphDatabase.driver(URI, auth=AUTH)

def get_subgraph_composition(driver):
    print("KOMPOSISI SIMPUL (NODES)")
   
    query_nodes = """
        MATCH (n)
        RETURN labels(n)[0] AS Jenis_Simpul, count(n) AS Jumlah
        ORDER BY Jumlah DESC
    """
    
    with driver.session() as session:
        result_nodes = session.run(query_nodes)
        for record in result_nodes:
            print(f"Simpul {record['Jenis_Simpul']}: {record['Jumlah']} buah")
            
    print("\nKOMPOSISI RELASI (EDGES)")
    
    query_rels = """
        MATCH ()-[r]->()
        RETURN type(r) AS Jenis_Relasi, count(r) AS Jumlah
        ORDER BY Jumlah DESC
    """
    
    with driver.session() as session:
        result_rels = session.run(query_rels)
        for record in result_rels:
            print(f"Relasi {record['Jenis_Relasi']}: {record['Jumlah']} buah")

    driver.close()

if __name__ == "__main__":
    get_subgraph_composition(driver)