from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from ingest import process_file
from query import rag_query
import os

app = FastAPI()

# API Endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    process_file(file_path)
    return {"status": "success"}

@app.get("/query")
async def query(q: str):
    results = rag_query(q)
    return {"results": results}

# frontend static files
# app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)