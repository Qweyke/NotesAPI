from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class CreateNoteResponse(BaseModel):
    id: int


class CreateNote(BaseModel):
    text: Optional[str] = None


class RegisterUserResponse(BaseModel):
    info: str
    name: Optional[str] = None


class RegisterUser(BaseModel):
    name: str
    password: str


class LogIn(BaseModel):
    name: str
    password: str


class LogInResponse(BaseModel):
    name: str
    token: str


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
