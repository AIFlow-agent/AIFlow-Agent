from llama_index import SimpleDirectoryReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    @staticmethod
    def load_and_process_documents(file_path: str):
        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        return texts