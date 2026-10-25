import pandas as pd
from neo4j import GraphDatabase
import datetime

URI = "bolt://127.0.0.1:7687"
AUTH = ("neo4j", "lintang123")

driver = GraphDatabase.driver(URI, auth=AUTH)

print("Mengambil data dari Neo4J")
with driver.session() as session:
 
    result = session.run("""
        MATCH (v:Visitor)-[r]->(i:Item) 
        RETURN v.visitorId AS visitorid, i.itemId AS itemid, r.timestamp AS timestamp, type(r) AS event
    """)
    df = pd.DataFrame([record.data() for record in result])
    driver.close()

print(f"Total data awal: {len(df)} baris")

df['tanggal'] = pd.to_datetime(df['timestamp'], unit='ms')

p1_mulai = '2015-05-18'
p1_akhir = '2015-05-31 23:59:59'
p2_mulai = '2015-08-16'
p2_akhir = '2015-08-31 23:59:59' 

df_p1 = df[(df['tanggal'] >= p1_mulai) & (df['tanggal'] <= p1_akhir)]
df_p2 = df[(df['tanggal'] >= p2_mulai) & (df['tanggal'] <= p2_akhir)]

print(f"Data P1 (Training): {len(df_p1)} baris")
print(f"Data P2 (Testing): {len(df_p2)} baris")

df_p1.to_csv('data_p1_training.csv', index=False)
df_p2.to_csv('data_p2_testing.csv', index=False)

print("Selesai! File 'data_p1_training.csv' dan 'data_p2_testing.csv' berhasil dibuat.")