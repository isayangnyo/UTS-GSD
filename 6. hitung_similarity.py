import pandas as pd
from neo4j import GraphDatabase
from sklearn.metrics.pairwise import cosine_similarity

URI = "bolt://127.0.0.1:7687"
AUTH = ("neo4j", "lintang123") 
driver = GraphDatabase.driver(URI, auth=AUTH)

print("Mengambil data untuk VSM")
query = """
    MATCH (v:Visitor)-[r]->(i:Item)
    WHERE r.timestamp >= 1431907200000 AND r.timestamp <= 1433116799000
    RETURN v.visitorId AS user, i.itemId AS item
    LIMIT 2000
"""
with driver.session() as session:
    result = session.run(query)
    df = pd.DataFrame([record.data() for record in result])

vsm_user = pd.crosstab(df['user'], df['item'])

print("Menghitung Cosine Similarity antar User")

sim_matrix = cosine_similarity(vsm_user)

sim_df = pd.DataFrame(sim_matrix, index=vsm_user.index, columns=vsm_user.index)

user_acuan = vsm_user.index[0] 
print(f"\nUser Acuan: {user_acuan}")

top_similar = sim_df[user_acuan].sort_values(ascending=False).head(6)
print("\n5 USER PALING MIRIP DENGAN USER ACUAN")

top_5 = top_similar.iloc[1:6]
print(top_5)

print("\nMenyimpan hasil similarity ke Neo4J")
with driver.session() as session:
    for target_user, score in top_5.items():
    
        query_simpan = """
            MATCH (u1:Visitor {visitorId: $user_acuan})
            MATCH (u2:Visitor {visitorId: $target_user})
            MERGE (u1)-[r:SIMILAR_TO]->(u2)
            SET r.score = $score
        """
        session.run(query_simpan, user_acuan=int(user_acuan), target_user=int(target_user), score=float(score))
        
print("Berhasil menyimpan relasi SIMILAR_TO ke database")

driver.close()