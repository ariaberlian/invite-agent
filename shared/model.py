from pydantic import BaseModel, Field
from typing import Optional

class InvitationInfo(BaseModel):
    user_name: str = ""
    agenda_name: str = ""
    location: str = ""
    scheduled_at: Optional[str] = ""
    notes: Optional[str] = ""
    recipients: list[str] = []
    tone: str = ""

class EmailModel(BaseModel):
    subject: str = ""
    body: str = ""
    recipients: list[str] = []

class ChatRequest(BaseModel):
    message: str
    user_id: str = "budigalaksi123"
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str