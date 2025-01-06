from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref


Base = declarative_base()


class SiaMessageModel(Base):
    __tablename__ = "message"

    id = Column(String, primary_key=True)
    conversation_id = Column(String)
    platform = Column(String, nullable=False)
    author = Column(String, nullable=False)
    content = Column(String, nullable=False)
    response_to = Column(String)
    message_type = Column(String, nullable=True)
    wen_posted = Column(DateTime, default=lambda: datetime.now())
    original_data = Column(JSON)
    flagged = Column(Boolean, nullable=True, default=False)
    message_metadata = Column(JSON)
    
    # Change relationship to load eagerly
    characters = relationship(
        "MessageCharacterModel",
        cascade="all, delete-orphan",
        lazy='joined'  # This makes it load eagerly by default
    )


class SiaCharacterSettingsModel(Base):
    __tablename__ = "character_settings"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    character_name_id = Column(String)
    character_settings = Column(JSON)


class MessageCharacterModel(Base):
    __tablename__ = "message_character"

    message_id = Column(String, ForeignKey('message.id'), primary_key=True)
    character_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)