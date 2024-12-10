import fastapi
from fastapi import Request

import models
from server import Server

server = Server()
app_router = fastapi.APIRouter()


@app_router.post("/users/register", response_model=models.RegisterUserResponse)
def register_user(request_body: models.RegisterUser):
    server.register_user(request_body.name, request_body.password)
    return models.RegisterUserResponse(info="Registered", name=request_body.name)


@app_router.get("/users/authorize", response_model=models.LogInResponse)
def log_in(request_body: models.LogIn):
    token = server.generate_jwt(request_body.name, request_body.password)

    return models.LogInResponse(name=request_body.name, token=token)


@app_router.post("/notes/new/{note_id}", response_model=models.CreateNoteResponse)
def create_note(note_id: int, request_body: models.CreateNote, request: Request):
    user_name = server.add_note(request.headers.get("Authorization"), note_id, request_body.text)
    return models.CreateNoteResponse(id=note_id, name=user_name)


@app_router.patch(
    "/notes/update/{note_id}", response_model=models.UpdateNoteTextResponse
)
def patch_note(note_id: int, request_body: models.UpdateNoteText, request: Request):
    user_name = server.update_note_data(
        request.headers.get("Authorization"), note_id, request_body.text
    )
    return models.UpdateNoteTextResponse(
        id=note_id,
        name=user_name
    )


@app_router.get("/notes/info/{note_id}", response_model=models.GetNoteInfoResponse)
def get_note_info(note_id: int, request: Request):
    note_data = server.get_note_data(request.headers.get("Authorization"), note_id)

    return models.GetNoteInfoResponse(id=note_id,
                                      created_at=note_data["created_at"], updated_at=note_data["updated_at"]
                                      )


@app_router.get("/notes/text/{note_id}", response_model=models.GetNoteTextResponse)
def get_note_text(note_id: int, request: Request):
    note_data = server.get_note_data(request.headers.get("Authorization"), note_id)

    return models.GetNoteTextResponse(id=note_data["id"], text=note_data["text"])


@app_router.delete("/notes/delete/{note_id}", response_model=models.DeleteNoteResponse)
def delete_note(note_id: int, request: Request):
    user_name = server.delete_note(request.headers.get("Authorization"), note_id)
    return models.DeleteNoteResponse(id=note_id, name=user_name)


@app_router.get("/notes/list", response_model=models.GetNotesListResponse)
def get_notes_list(request: Request):
    return models.GetNotesListResponse(
        notes_ids=server.get_notes_list(request.headers.get("Authorization"))
    )
