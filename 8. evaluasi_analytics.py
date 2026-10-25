import pandas as pd
from neo4j import GraphDatabase
import numpy as np

URI = "bolt://127.0.0.1:7687"
AUTH = ("neo4j", "lintang123") 
driver = GraphDatabase.driver(URI, auth=AUTH)

user_acuan = 1111394
rekomendasi_items = [198798, 29100, 76196]

print("Mengecek histori interaksi User di Periode Testing (P2)")
query_testing = """
    MATCH (v:Visitor)-[r]->(i:Item)
    WHERE v.visitorId = $user_id 
      AND i.itemId IN $items
      AND r.timestamp >= 1439683200000 AND r.timestamp <= 1441065599000
    RETURN i.itemId AS item_id
"""

with driver.session() as session:
    result = session.run(query_testing, user_id=user_acuan, items=rekomendasi_items)
    ground_truth = [record["item_id"] for record in result]

print(f"Item Rekomendasi: {rekomendasi_items}")
print(f"Item yang benar-benar dilihat User {user_acuan} di P2: {ground_truth}")

hit = 1 if any(item in ground_truth for item in rekomendasi_items) else 0
print(f"\n=> Hit@5: {hit}")

def calculate_ndcg(recommendations, actual_interactions, k=5):
    dcg = 0.0
    for i, item in enumerate(recommendations[:k]):
        if item in actual_interactions:
            dcg += 1 / np.log2(i + 2) 
            
    idcg = 0.0
    for i in range(min(len(actual_interactions), k)):
        idcg += 1 / np.log2(i + 2)
            
    if idcg == 0:
        return 0.0
    return dcg / idcg

ndcg = calculate_ndcg(rekomendasi_items, ground_truth, k=5)
print(f"=> NDCG@5: {ndcg:.4f}")

driver.close()