from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class KnowledgeModuleSettingsModel(Base):
    __tablename__ = "knowledge_module_settings"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    character_name_id = Column(String)
    module_name = Column(String)
    module_settings = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now())
