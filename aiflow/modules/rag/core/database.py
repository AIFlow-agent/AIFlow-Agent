import psycopg2
from config import Config

class Database:
    @staticmethod
    def get_connection():
        return psycopg2.connect(**Config.get_postgres_config())

    @staticmethod
    def store_document_metadata(file_name: str, file_path: str) -> int:
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO documents (file_name, file_path) VALUES (%s, %s) RETURNING id",
            (file_name, file_path)
        )
        doc_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return doc_id

    @staticmethod
    def get_document_metadata(doc_id: int):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM documents WHERE id = %s", (doc_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result

    @staticmethod
    def delete_document_metadata(doc_id: int):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
        conn.commit()
        cur.close()
        conn.close()