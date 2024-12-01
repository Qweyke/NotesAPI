from datetime import datetime

import fastapi
from fastapi import Request

import model
from src.auth_manager import AuthorizationManager
from src.notes_manager import NotesManager

notes_manager = NotesManager()
authorization_manager = AuthorizationManager()

app_router = fastapi.APIRouter()


@app_router.post("/users/", response_model=model.RegisterUserResponse)
def register_user(request_body: model.RegisterUser):
    authorization_manager.register_user(request_body.name, request_body.password)
    return model.RegisterUserResponse(info="Registered", name=request_body.name)


@app_router.post("/notes/{note_id}", response_model=model.CreateNoteResponse)
def create_note(note_id: int, request_body: model.CreateNote, request: Request):
    authorization_manager.verify_jwt(request)
    notes_manager.add_note(note_id, request_body.text)
    return model.CreateNoteResponse(id=note_id)


@app_router.patch("/notes/{note_id}", response_model=model.UpdateNoteTextResponse)
def create_note(note_id: int, request_body: model.UpdateNoteText, request: Request):
    authorization_manager.verify_jwt(request)
    note_data = notes_manager.get_note_data(note_id)
    note_data["text"] = request_body.text
    note_data["updated_at"] = datetime.now()

    notes_manager.update_note_data(note_id, note_data)

    return model.UpdateNoteTextResponse(
        id=note_data["id"], text=note_data["text"], updated_at=note_data["updated_at"]
    )


@app_router.get("/users/", response_model=model.LogInResponse)
def log_in(request_body: model.LogIn):
    token = authorization_manager.generate_jwt(request_body.name, request_body.password)

    return model.LogInResponse(name=request_body.name, token=token)


@app_router.get("/notes/{note_id}/info", response_model=model.GetNoteInfoResponse)
def get_note_info(note_id: int, request: Request):
    authorization_manager.verify_jwt(request)
    note_data = notes_manager.get_note_data(note_id)

    return model.GetNoteInfoResponse(
        created_at=note_data["created_at"], updated_at=note_data["updated_at"]
    )


@app_router.get("/notes/{note_id}/text", response_model=model.GetNoteTextResponse)
def get_note_text(note_id: int, request: Request):
    authorization_manager.verify_jwt(request)
    note_data = notes_manager.get_note_data(note_id)

    return model.GetNoteTextResponse(id=note_data["id"], text=note_data["text"])


@app_router.get("/notes/list", response_model=model.GetNotesListResponse)
def get_notes_list(request: Request):
    authorization_manager.verify_jwt(request)
    return model.GetNotesListResponse(notes_ids=notes_manager.get_notes_list())


@app_router.delete("/notes/{note_id}", response_model=model.DeleteNoteResponse)
def delete_note(note_id: int, request: Request):
    authorization_manager.verify_jwt(request)
    notes_manager.delete_note(note_id)
    return model.DeleteNoteResponse(id=note_id, deleted_at=datetime.now())
