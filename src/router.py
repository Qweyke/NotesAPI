from datetime import datetime

import fastapi

import model
from src.notes_manager import NotesManager

notes_manager = NotesManager()
app_router = fastapi.APIRouter()


@app_router.post("/notes/{note_id}", response_model=model.CreateNoteResponse)
def create_note(note_id: int, request_body: model.CreateNote):
    notes_manager.add_note(note_id, request_body.text)
    return model.CreateNoteResponse(id=note_id)


@app_router.patch("/notes/{note_id}", response_model=model.UpdateNoteTextResponse)
def create_note(note_id: int, request_body: model.UpdateNoteText):
    note_data = notes_manager.get_note_data(note_id)
    note_data["text"] = request_body.text
    note_data["updated_at"] = datetime.now()

    notes_manager.update_note_data(note_id, note_data)

    return model.UpdateNoteTextResponse(id=note_data["id"], text=note_data["text"], updated_at=note_data["updated_at"])


@app_router.get("/notes/{note_id}/info", response_model=model.GetNoteInfoResponse)
def get_note_info(note_id: int):
    note_data = notes_manager.get_note_data(note_id)

    return model.GetNoteInfoResponse(created_at=note_data["created_at"], updated_at=note_data["updated_at"])


@app_router.get("/notes/{note_id}/text", response_model=model.GetNoteTextResponse)
def get_note_text(note_id: int):
    note_data = notes_manager.get_note_data(note_id)

    return model.GetNoteTextResponse(id=note_data["id"], text=note_data["text"])


@app_router.delete("/notes/{note_id}", response_model=model.DeleteNoteResponse)
def delete_note(note_id: int):
    return model.DeleteNoteResponse(id=note_id, deleted_at=datetime.now())


@app_router.get("/notes/list", response_model=model.GetNotesListResponse)
def get_notes_list():
    return model.GetNotesListResponse(notes_ids=notes_manager.get_notes_list())