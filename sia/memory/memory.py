import textwrap

from sqlalchemy import asc, create_engine, desc
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from sia.character import SiaCharacter
from utils.logging_utils import enable_logging, log_message, setup_logging

from .models_db import Base, SiaCharacterSettingsModel, SiaMessageModel, MessageCharacterModel
from .schemas import (
    SiaCharacterSettingsSchema,
    SiaMessageGeneratedSchema,
    SiaMessageSchema,
)


class SiaMemory:

    def __init__(self, db_path: str, character: SiaCharacter):
        self.db_path = db_path
        self.character = character
        self.engine = create_engine(self.db_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.logging_enabled = self.character.logging_enabled

        self.logger = setup_logging()
        enable_logging(self.logging_enabled)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    def get_messages(
        self,
        id=None,
        platform: str = None,
        author: str = None,
        not_author: str = None,
        character: str = None,
        conversation_id: str = None,
        response_to: str = None,
        flagged: int = 0,
        sort_by: str = None,
        sort_order: str = "asc",
        is_post: bool = None,
        from_datetime=None,
        exclude_own_conversations: bool = False,
    ):
        with self.session_scope() as session:
            # Start with a query that eagerly loads characters
            query = session.query(SiaMessageModel)
            
            if character:
                # Use subquery for character filtering
                character_messages = (
                    session.query(MessageCharacterModel.message_id)
                    .filter(MessageCharacterModel.character_name == character)
                    .subquery()
                )
                query = query.filter(SiaMessageModel.id.in_(character_messages.select()))
            
            # Apply other filters
            if id:
                query = query.filter_by(id=id)
            if platform:
                query = query.filter_by(platform=platform)
            if author:
                query = query.filter_by(author=author)
            if not_author:
                query = query.filter(SiaMessageModel.author != not_author)
            if conversation_id:
                query = query.filter_by(conversation_id=conversation_id)
            if response_to:
                if response_to == "NOT NULL":
                    query = query.filter(SiaMessageModel.response_to != None)
                else:
                    query = query.filter_by(response_to=response_to)
            if from_datetime:
                query = query.filter(SiaMessageModel.wen_posted >= from_datetime)
            if is_post:
                query = query.filter(SiaMessageModel.message_type == "post")
            if flagged != 2:
                query = query.filter_by(flagged=bool(flagged))

            # Handle sorting
            if sort_by:
                order_func = asc if sort_order == "asc" else desc
                query = query.order_by(order_func(sort_by))

            # Execute query and convert to schema
            messages = query.all()
            return [SiaMessageSchema.from_orm(message) for message in messages]

    def add_message(
        self,
        message_id: str,
        message: SiaMessageGeneratedSchema,
        message_type: str = None,
        original_data: dict = None,
        character: str = None,
    ) -> SiaMessageSchema:
        with self.session_scope() as session:
            try:
                # First check if message exists
                existing_message = session.query(SiaMessageModel).filter_by(id=str(message_id)).first()
                if existing_message:
                    # Check if character association exists
                    character_name = character or self.character.name
                    existing_link = session.query(MessageCharacterModel).filter_by(
                        message_id=str(message_id),
                        character_name=character_name
                    ).first()
                    
                    if existing_link:
                        # Both message and link exist, return existing message
                        return SiaMessageSchema.from_orm(existing_message)
                    
                    # Message exists but link doesn't - create new link
                    character_model = MessageCharacterModel(
                        message_id=str(message_id),
                        character_name=character_name,
                        created_at=existing_message.wen_posted
                    )
                    session.add(character_model)
                    session.commit()
                    return SiaMessageSchema.from_orm(existing_message)

                # Message doesn't exist - create new message and link
                message_model = SiaMessageModel(
                    id=str(message_id),
                    platform=message.platform,
                    author=message.author,
                    content=message.content,
                    conversation_id=message.conversation_id or message_id,
                    response_to=message.response_to,
                    flagged=message.flagged,
                    message_metadata=message.message_metadata,
                    original_data=original_data,
                    message_type=message_type
                )
                session.add(message_model)
                session.flush()  # Ensure message is created before creating link
                
                # Create character association
                character_model = MessageCharacterModel(
                    message_id=str(message_id),
                    character_name=character or self.character.name,
                    created_at=message_model.wen_posted
                )
                session.add(character_model)
                session.commit()
                
                return SiaMessageSchema.from_orm(message_model)
                
            except Exception as e:
                log_message(self.logger, "error", self, f"Error in add_message: {e}")
                session.rollback()
                # Return existing message if we can find it
                existing_message = session.query(SiaMessageModel).filter_by(id=str(message_id)).first()
                if existing_message:
                    return SiaMessageSchema.from_orm(existing_message)
                raise e
    
    def get_conversation_ids(self):
        session = self.Session()
        conversation_ids = (
            session.query(SiaMessageModel.conversation_id)
            .filter(SiaMessageModel.id != SiaMessageModel.conversation_id)
            .distinct()
            .all()
        )
        session.close()
        return [conversation_id[0] for conversation_id in conversation_ids]

    def clear_messages(self):
        session = self.Session()
        try:
            # Find all message IDs associated with this character
            message_ids = (
                session.query(SiaMessageModel.id)
                .join(MessageCharacterModel)
                .filter(MessageCharacterModel.character_name == self.character.name)
                .all()
            )
            
            # Delete the messages
            if message_ids:
                message_ids = [id[0] for id in message_ids]
                session.query(SiaMessageModel)\
                    .filter(SiaMessageModel.id.in_(message_ids))\
                    .delete(synchronize_session=False)
                
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
    def reset_database(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    @classmethod
    def printable_message(
        self,
        message_id,
        author_username,
        created_at,
        text,
        wrap_width=70,
        indent_width=5,
    ):
        output_str = ""
        output_str += f"{author_username} [{created_at}] (message id: {message_id}):\n"
        wrapped_comment = textwrap.fill(text.strip(), width=wrap_width)
        output_str += (
            " " * indent_width
            + wrapped_comment.replace("\n", "\n" + " " * indent_width)
            + "\n"
        )

        return output_str

    @classmethod
    def printable_messages_list(self, messages):
        output_str = ""
        for message in messages:
            message_id = message.id

            output_str += self.printable_message(
                message_id=message_id,
                author_username=message.author,
                created_at=message.wen_posted,
                text=message.content,
            )

            output_str += f"\n\n{'=' * 10}\n\n"

        return output_str

    def get_character_settings(self):
        session = self.Session()
        try:
            character_settings = (
                session.query(SiaCharacterSettingsModel)
                .filter_by(character_name_id=self.character.name_id)
                .first()
            )
            if not character_settings:
                character_settings = SiaCharacterSettingsModel(
                    character_name_id=self.character.name_id, character_settings={}
                )
                session.add(character_settings)
                session.commit()

            # Convert the SQLAlchemy model to a Pydantic schema before closing
            # the session
            character_settings_schema = SiaCharacterSettingsSchema.from_orm(
                character_settings
            )
            return character_settings_schema

        finally:
            session.close()

    def update_character_settings(self, character_settings: SiaCharacterSettingsSchema):
        session = self.Session()
        # Convert the Pydantic schema to a dictionary
        character_settings_dict = character_settings.dict(exclude_unset=True)
        session.query(SiaCharacterSettingsModel).filter_by(
            character_name_id=self.character.name_id
        ).update(character_settings_dict)
        session.commit()
        session.close()
