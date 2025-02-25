from fastapi import FastAPI, UploadFile, File, HTTPException
from datetime import datetime
import os
from core.database import Database
from core.document_processor import DocumentProcessor
from core.vector_store import VectorStore
from models.models import DocumentUpload, DocumentResponse
from config import Config

app = FastAPI()
vector_store = VectorStore()

@app.post("/upload/", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are allowed")
    
    # 保存文件到临时目录
    file_path = f"{Config.TEMP_DIR}/{file.filename}"
    os.makedirs(Config.TEMP_DIR, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # 处理文档并生成嵌入
    texts = DocumentProcessor.load_and_process_documents(file_path)
    for text in texts:
        vector_store.add_documents([text])
    
    # 存储文档元数据
    doc_id = Database.store_document_metadata(file.filename, file_path)
    
    return {"id": doc_id, "file_name": file.filename, "file_path": file_path, "created_at": datetime.now()}

@app.get("/document/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: int):
    metadata = Database.get_document_metadata(doc_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"id": metadata[0], "file_name": metadata[1], "file_path": metadata[2], "created_at": metadata[3]}

@app.delete("/document/{doc_id}")
async def delete_document(doc_id: int):
    metadata = Database.get_document_metadata(doc_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # 删除文档文件
    if os.path.exists(metadata[2]):
        os.remove(metadata[2])
    
    # 删除元数据
    Database.delete_document_metadata(doc_id)
    
    return {"message": "Document deleted successfully"}

@app.post("/query/")
async def query_documents(query: str):
    results = vector_store.similarity_search(query, k=5)
    return {"results": [result.page_content for result in results]}