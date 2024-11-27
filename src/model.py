from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class CreateNoteResponse(BaseModel):
    id: int


class CreateNote(BaseModel):
    text: Optional[str] = None


class UpdateNoteText(BaseModel):
    text: Optional[str] = None


class UpdateNoteTextResponse(BaseModel):
    id: int
    text: str
    updated_at: datetime


class GetNoteTextResponse(BaseModel):
    id: int
    text: str


class GetNoteInfoResponse(BaseModel):
    created_at: datetime
    updated_at: datetime


class GetNotesListResponse(BaseModel):
    notes_ids: Dict[int, int]


class DeleteNoteResponse(BaseModel):
    id: int
    deleted_at: datetime
