from pydantic import BaseModel
from datetime import datetime

class DocumentUpload(BaseModel):
    file_name: str
    file_content: str

class DocumentResponse(BaseModel):
    id: int
    file_name: str
    file_path: str
    created_at: datetime