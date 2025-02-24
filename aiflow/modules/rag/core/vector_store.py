from llama_index.vector_stores import FAISSVectorStore
from langchain.embeddings import HuggingFaceEmbeddings

class VectorStore:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings()
        self.vector_store = FAISSVectorStore.from_documents([], self.embeddings)

    def add_documents(self, texts):
        self.vector_store.add_documents(texts)

    def similarity_search(self, query: str, k: int = 5):
        return self.vector_store.similarity_search(query, k=k)