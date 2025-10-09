from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

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