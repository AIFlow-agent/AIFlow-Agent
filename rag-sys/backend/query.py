import os
import psycopg2
import faiss
from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector
from langchain_openai import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

# 设置 OpenAI API 密钥
os.environ["OPENAI_API_KEY"] = ""
model = SentenceTransformer('all-mpnet-base-v2')


def create_faiss_index(conn):
    # 获取所有文档的嵌入
    cur = conn.cursor()
    cur.execute("SELECT id, embedding FROM document_embeddings")
    rows = cur.fetchall()
    
    embeddings = [np.frombuffer(row[1], dtype=np.float32) for row in rows]
    embeddings = np.stack(embeddings)  

    dim = embeddings.shape[1] 
    index = faiss.IndexFlatL2(dim)  
    index.add(embeddings)  
    return index

def query_faiss_index(query, index, conn):
    embeddings = OpenAIEmbeddings() 
    query_embedding = embeddings.embed_documents([query])[0]
    
    query_embedding = np.array(query_embedding).astype(np.float32)

    D, I = index.search(np.expand_dims(query_embedding, axis=0), k=5)  
    
    cur = conn.cursor()
    relevant_documents = []
    for idx in I[0]:
        cur.execute("SELECT content FROM documents WHERE id = %s;", (idx,))
        result = cur.fetchone()
        relevant_documents.append(result[0])
    
    return relevant_documents

def generate_answer_from_openai(query, context):
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "You are a professional knowledge assistant, please answer the question based on the following context：\n{context}"
        ),
        HumanMessagePromptTemplate.from_template(
            "Question：{question}\nPlease give a detailed answer："
        )
    ])
    formatted_messages = prompt_template.format_messages(
        context=context,
        question=query
    )
    
    chat = ChatOpenAI(temperature=0)
    response = chat.invoke(formatted_messages)
    return response.content


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
        
        context_parts = [
            f"[similarity:{similarity:.2f}] {content}"
            for content, similarity in cur.fetchall()
        ]
        context = '\n'.join(context_parts)
        
        return generate_answer_from_openai(question, context)
    finally:
        conn.close()

