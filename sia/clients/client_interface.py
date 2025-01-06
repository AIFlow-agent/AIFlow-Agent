from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
from sia.memory.schemas import SiaMessageGeneratedSchema, SiaMessageSchema


class SiaClientInterface(ABC):
    """Abstract interface class for Sia clients (Twitter, Telegram, etc.)"""
    
    platform_name: str
    
    @abstractmethod
    def __init__(self, sia, logging_enabled: bool = True, **kwargs):
        """Initialize the client"""
        self.sia = sia
        self.logging_enabled = logging_enabled
    

    @abstractmethod
    async def run(self):
        """Main loop to run the client"""
        pass
    

    # publish message
    def publish_message(self, message: SiaMessageGeneratedSchema, media: Optional[List[str]] = None, in_reply_to_message_id: Optional[str] = None):
        """Publish a message to the platform"""
        pass

    # posting loop
    def post(self):
        """Check if it's time to post and if so, post the message"""
        pass

    # reply loop
    def reply(self):
        """Check if there are new messages to reply to and if the conditions are met, then reply to them"""
        pass

    # engagement loop
    def engage(self):
        """Check if there are new messages to engage with and if the conditions are met, then engage with them"""
        pass
