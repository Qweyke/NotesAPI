import fastapi
from fastapi import Request

import model
from src.server import Server

server = Server()
app_router = fastapi.APIRouter()


@app_router.post("/users/register", response_model=model.RegisterUserResponse)
def register_user(request_body: model.RegisterUser):
    server.register_user(request_body.name, request_body.password)
    return model.RegisterUserResponse(info="Registered", name=request_body.name)


@app_router.get("/users/authorize", response_model=model.LogInResponse)
def log_in(request_body: model.LogIn):
    token = server.generate_jwt(request_body.name, request_body.password)

    return model.LogInResponse(name=request_body.name, token=token)


@app_router.post("/notes/new/{note_id}", response_model=model.CreateNoteResponse)
def create_note(note_id: int, request_body: model.CreateNote, request: Request):
    server.add_note(request.headers.get("Authorization"), note_id, request_body.text)
    return model.CreateNoteResponse(id=note_id)


@app_router.patch(
    "/notes/update/{note_id}", response_model=model.UpdateNoteTextResponse
)
def patch_note(note_id: int, request_body: model.UpdateNoteText, request: Request):
    updated_note = server.update_note_data(
        request.headers.get("Authorization"), note_id, request_body.text
    )
    return model.UpdateNoteTextResponse(
        id=updated_note["id"],
        text=updated_note["text"],
        updated_at=updated_note["updated_at"],
    )


@app_router.get("/notes/info/{note_id}", response_model=model.GetNoteInfoResponse)
def get_note_info(note_id: int, request: Request):
    note_data = server.get_note_data(request.headers.get("Authorization"), note_id)

    return model.GetNoteInfoResponse(
        created_at=note_data["created_at"], updated_at=note_data["updated_at"]
    )


@app_router.get("/notes/text/{note_id}", response_model=model.GetNoteTextResponse)
def get_note_text(note_id: int, request: Request):
    note_data = server.get_note_data(request.headers.get("Authorization"), note_id)

    return model.GetNoteTextResponse(id=note_data["id"], text=note_data["text"])


@app_router.delete("/notes/delete/{note_id}", response_model=model.DeleteNoteResponse)
def delete_note(note_id: int, request: Request):
    time = server.delete_note(request.headers.get("Authorization"), note_id)
    return model.DeleteNoteResponse(id=note_id, deleted_at=time)


@app_router.get("/notes/list", response_model=model.GetNotesListResponse)
def get_notes_list(request: Request):
    return model.GetNotesListResponse(
        notes_ids=server.get_notes_list(request.headers.get("Authorization"))
    )
