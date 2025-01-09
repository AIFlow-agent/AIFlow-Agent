from pydantic import BaseModel


class ResponseFilteringResultLLMSchema(BaseModel):
    should_respond: bool
    reason: str
