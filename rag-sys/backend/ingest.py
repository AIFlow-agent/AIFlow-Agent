from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import psycopg2
import numpy as np
from psycopg2.extras import Json  
from config import Config

model = SentenceTransformer('all-mpnet-base-v2')

def process_file(file_path: str):

    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(docs)

    conn = psycopg2.connect(**Config.get_postgres_config())    
    try:
        cur = conn.cursor()
        for chunk in chunks:
 
            embedding = model.encode(chunk.page_content)
            
            cur.execute(
                """INSERT INTO documents (content, embedding, metadata)
                   VALUES (%s, %s, %s)""",
                (chunk.page_content, 
                 embedding.tolist(),
                 Json({"source": file_path})) 
            )
        conn.commit()
    finally:
        conn.close()
        