import textwrap
from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class SiaMessageGeneratedSchema(BaseModel):
    conversation_id: Optional[str] = None
    content: str
    platform: str
    author: str
    response_to: Optional[str] = None
    flagged: Optional[bool] = Field(default=False)
    message_metadata: Optional[dict] = None

    class Config:
        # orm_mode = True
        from_attributes = True


class SiaMessageSchema(SiaMessageGeneratedSchema):
    id: str
    message_type: Optional[str] = Field(default="post")  # Can be "post" or "reply"
    wen_posted: datetime = Field(default_factory=lambda: datetime.now())
    original_data: Optional[dict] = None
    
    characters: list['MessageCharacterSchema'] = Field(default_factory=list)

    @classmethod
    def from_orm(cls, obj):
        # Get all column values
        values = {
            c.name: getattr(obj, c.name)
            for c in obj.__table__.columns
        }
        
        # Handle characters relationship explicitly
        try:
            if hasattr(obj, 'characters'):
                values['characters'] = [
                    MessageCharacterSchema(
                        message_id=char.message_id,
                        character_name=char.character_name,
                        created_at=char.created_at
                    )
                    for char in (obj.characters or [])
                ]
        except Exception:
            values['characters'] = []
            
        return cls(**values)

    def printable(self):
        output_str = ""
        output_str += f"{self.author} [{self.wen_posted}] (id: {self.id}):\n"
        wrapped_content = textwrap.fill(self.content.strip(), width=70)
        output_str += " " * 5 + wrapped_content.replace("\n", "\n" + " " * 5) + "\n"
        return output_str

    def printable_list(self, messages):
        output_str = ""
        for message in messages:
            output_str += message.printable() + "\n\n" + "=" * 10 + "\n\n"
        return output_str

    def select_by_id_from_list(self, messages, id):
        return next((message for message in messages if message.id == id), None)

    class Config:
        # orm_mode = True
        from_attributes = True


class MessageCharacterSchema(BaseModel):
    message_id: str
    character_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now())

    class Config:
        from_attributes = True


class SiaCharacterSettingsSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    character_name_id: str
    character_settings: dict

    class Config:
        # orm_mode = True
        from_attributes = True
