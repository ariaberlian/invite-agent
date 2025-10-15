from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserContext(BaseModel):
    username: str = ""
    full_name: str = ""
    user_id: str = ""

class InvitationInfo(BaseModel):
    agenda_name: str = ""
    location: str = ""
    scheduled_at: Optional[str] = ""
    notes: Optional[str] = ""
    recipients: list[str] = []
    tone: str = ""

class EmailModel(BaseModel):
    subject: str = ""
    body: str = ""
    email_recipients: list[str] = []

class ChatRequest(BaseModel):
    message: str
    user_id: str = ""
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

class SessionInfo(BaseModel):
    session_id: str
    created_at: datetime
    updated_at: datetime
    preview: Optional[str] = None  # Preview of last message or conversation

class SessionListResponse(BaseModel):
    sessions: list[SessionInfo]

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class ChatHistoryResponse(BaseModel):
    messages: list[ChatMessage]
    session_id: str