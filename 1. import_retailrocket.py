import argparse
import os
import sys

import pandas as pd
from neo4j import GraphDatabase
from tqdm import tqdm


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Impor dataset RetailRocket (events.csv) ke database Neo4J."
    )
    parser.add_argument("-u", "--user", default="neo4j", help="Username Neo4j (default: neo4j)")
    parser.add_argument("-p", "--password", default="lintang123", help="Password Neo4J (default: neo4j)") 
    parser.add_argument("-b", "--bolt", default="bolt://127.0.0.1:7687", help="Neo4J URI / Bolt") 
    parser.add_argument("-s", "--source", default="ecommerce-dataset", help="Direktori/folder sumber data")
    parser.add_argument("--batch-size", type=int, default=5000, help="Ukuran batch impor")
    return parser.parse_args()


def create_constraints(session):
    """Bikin index/constraint biar MERGE cepat & unik."""
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (v:Visitor) REQUIRE v.visitorId IS UNIQUE")
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (i:Item) REQUIRE i.itemId IS UNIQUE")


def import_batch(tx, batch):
    cypher_query = """
    UNWIND $batch AS row
    MERGE (v:Visitor {visitorId: row.visitorid})
    MERGE (i:Item {itemId: row.itemid})
    WITH v, i, row
    CALL {
        WITH v, i, row
        WITH v, i, row WHERE row.event = 'view'
        CREATE (v)-[:VIEWED {timestamp: row.timestamp}]->(i)
        RETURN count(*) AS _
        UNION ALL
        WITH v, i, row
        WITH v, i, row WHERE row.event = 'addtocart'
        CREATE (v)-[:ADDED_TO_CART {timestamp: row.timestamp}]->(i)
        RETURN count(*) AS _
        UNION ALL
        WITH v, i, row
        WITH v, i, row WHERE row.event = 'transaction'
        CREATE (v)-[:BOUGHT {timestamp: row.timestamp, transactionId: row.transactionid}]->(i)
        RETURN count(*) AS _
    }
    RETURN count(*) AS total_processed
    """
    tx.run(cypher_query, batch=batch)


def main():
    args = parse_arguments()

    csv_file_path = os.path.join(args.source, "events.csv")
    if not os.path.exists(csv_file_path):
        print(f"Error: File '{csv_file_path}' tidak ditemukan!")
        sys.exit(1)

    try:
        driver = GraphDatabase.driver(args.bolt, auth=(args.user, args.password))
        driver.verify_connectivity()
        print(f"Berhasil terhubung ke {args.bolt}")
    except Exception as e:
        print(f"Gagal terhubung ke database: {e}")
        sys.exit(1)

    batch_size = args.batch_size

    with driver.session() as session:
        create_constraints(session)

        print(f"Membaca file data dari: {csv_file_path}")
      
        total_rows = sum(1 for _ in open(csv_file_path, "r", encoding="utf-8")) - 1
        total_chunks = (total_rows // batch_size) + 1
        print(f"Total baris (excl. header): {total_rows}, total batch: {total_chunks}")

        chunks = pd.read_csv(csv_file_path, chunksize=batch_size)

        print("Memulai proses impor data ke Neo4j...")
        for chunk in tqdm(chunks, total=total_chunks, desc="Mengimpor Batch Data"):
        
            chunk["transactionid"] = chunk["transactionid"].fillna("").astype(str)
           
            chunk = chunk.rename(columns={
                "visitorid": "visitorid",
                "itemid": "itemid",
                "timestamp": "timestamp",
                "event": "event",
                "transactionid": "transactionid",
            })
            records = chunk.to_dict(orient="records")
            session.execute_write(import_batch, records)

    driver.close()
    print("Proses impor berhasil.")


if __name__ == "__main__":
    main()
