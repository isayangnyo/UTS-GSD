import pandas as pd
from neo4j import GraphDatabase

URI = "bolt://127.0.0.1:7687"
AUTH = ("neo4j", "lintang123") 
driver = GraphDatabase.driver(URI, auth=AUTH)

print("Mengambil data sampel dari Neo4J...")

query_vsm_item = """
    MATCH (v:Visitor)-[r]->(i:Item)
    WHERE r.timestamp >= 1431907200000 AND r.timestamp <= 1433116799000
    RETURN v.visitorId AS user, i.itemId AS item
    LIMIT 2000
"""

with driver.session() as session:
    result = session.run(query_vsm_item)
    df_vsm = pd.DataFrame([record.data() for record in result])
driver.close()

vsm_item_matrix = pd.crosstab(df_vsm['item'], df_vsm['user'])

print("\nKARAKTERISTIK VSM ITEM")
print(f"Dimensi Shape: {vsm_item_matrix.shape}")
print(f"Artinya: Ada {vsm_item_matrix.shape[0]} Item (baris) dan {vsm_item_matrix.shape[1]} User (kolom).")

print("\nContoh 5 baris pertama Matriks:")
print(vsm_item_matrix.head())

total_cells = vsm_item_matrix.shape[0] * vsm_item_matrix.shape[1]
non_zero_cells = (vsm_item_matrix > 0).sum().sum()
sparsity = (1 - (non_zero_cells / total_cells)) * 100
print(f"\nTingkat Sparsity: {sparsity:.2f}%")
 