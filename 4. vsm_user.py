import pandas as pd
from neo4j import GraphDatabase

URI = "bolt://127.0.0.1:7687"
AUTH = ("neo4j", "lintang123") 
driver = GraphDatabase.driver(URI, auth=AUTH)

print("Mengambil data sampel dari Neo4J")

query_vsm_user = """
    MATCH (v:Visitor)-[r]->(i:Item)
    WHERE r.timestamp >= 1431907200000 AND r.timestamp <= 1433116799000
    RETURN v.visitorId AS user, i.itemId AS item
    LIMIT 2000
"""

with driver.session() as session:
    result = session.run(query_vsm_user)
    df_vsm = pd.DataFrame([record.data() for record in result])
driver.close()

vsm_user_matrix = pd.crosstab(df_vsm['user'], df_vsm['item'])

print("\nKARAKTERISTIK VSM USER")
print(f"Dimensi Shape: {vsm_user_matrix.shape}")
print(f"Artinya: Ada {vsm_user_matrix.shape[0]} User (baris) dan {vsm_user_matrix.shape[1]} Item (kolom).")

print("\nContoh 5 baris pertama Matriks:")
print(vsm_user_matrix.head())

total_cells = vsm_user_matrix.shape[0] * vsm_user_matrix.shape[1]
non_zero_cells = (vsm_user_matrix > 0).sum().sum()
sparsity = (1 - (non_zero_cells / total_cells)) * 100
print(f"\nTingkat Sparsity: {sparsity:.2f}% (Matriks sangat jarang karena mayoritas isinya 0)")
