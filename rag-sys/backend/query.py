from sentence_transformers import SentenceTransformer
import psycopg2
from pgvector.psycopg2 import register_vector
from config import Config

model = SentenceTransformer('all-mpnet-base-v2')

def rag_query(question: str, top_k=3):
    query_embedding = model.encode(question)
    
    conn = psycopg2.connect(**Config.get_postgres_config())
    register_vector(conn)
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT content, 1 - (embedding <=> %s) AS similarity
            FROM documents
            ORDER BY similarity DESC
            LIMIT %s
        """, (query_embedding, top_k))
        
        return [
            {"content": row[0], "similarity": float(row[1])}
            for row in cur.fetchall()
        ]
    finally:
        conn.close()