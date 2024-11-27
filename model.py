from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Optional


class CreateNoteResponse(BaseModel):
    id: int
    text: Optional[str] = None


class GetNodeResponse(BaseModel):
    id: int
    text: str


class NoteInfoResponse(BaseModel):
    created_at: datetime
    updated_at: datetime


class NotesListResponse(BaseModel):
    notes_ids: Dict[int, int]


