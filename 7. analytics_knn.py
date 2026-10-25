import pandas as pd
import numpy as np
from neo4j import GraphDatabase
from sklearn.metrics.pairwise import cosine_similarity
import random

URI = "bolt://127.0.0.1:7687"
AUTH = ("neo4j", "lintang123") 
driver = GraphDatabase.driver(URI, auth=AUTH)

query = """
    MATCH (v:Visitor)-[r]->(i:Item)
    WHERE r.timestamp >= 1431907200000 AND r.timestamp <= 1433116799000
    RETURN v.visitorId AS user, i.itemId AS item
    LIMIT 10000
"""
with driver.session() as session:
    result = session.run(query)
    df = pd.DataFrame([record.data() for record in result])

vsm_user = pd.crosstab(df['user'], df['item'])

random.seed(42) 
user_list = list(vsm_user.index)
user_acuan = random.choice(user_list)
print(f"User Acuan yang dipilih secara acak: {user_acuan}")

sim_matrix = cosine_similarity(vsm_user)
sim_df = pd.DataFrame(sim_matrix, index=vsm_user.index, columns=vsm_user.index)

top_knn = sim_df[user_acuan].sort_values(ascending=False).iloc[1:6]
print("\n5 User KNN terdekat:")
print(top_knn)

kandidat_item = pd.Series(dtype=float)
for knn_user, sim_score in top_knn.items():
    item_knn = vsm_user.loc[knn_user]
    item_knn = item_knn[item_knn > 0]
    kandidat_item = pd.concat([kandidat_item, item_knn * sim_score])

rekomendasi_item = kandidat_item.groupby(kandidat_item.index).sum().sort_values(ascending=False)


top_3_item = rekomendasi_item.head(3)

print("\n3 ITEM YANG DIREKOMENDASIKAN (IKLAN)")
for i, (item_id, score) in enumerate(top_3_item.items(), 1):
    print(f"{i}. Item ID: {item_id} (Skor Relevansi: {score:.4f})")

driver.close()