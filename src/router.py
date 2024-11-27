import json
import os
from datetime import datetime

import fastapi

import model
from src import counter_manager
from src.main import counter_manager

app_router = fastapi.APIRouter()


def get_note_data(note_id: int):
    note_path = f"notes/note{note_id}.json"

    if not os.path.exists(note_path):
        raise fastapi.HTTPException(status_code=404, detail="Note not found")

    with open(note_path, "r") as note_file:
        note_data = json.load(note_file)

    return note_data


@app_router.post("/notes", response_model=model.CreateNoteResponse)
def create_note(note: model.CreateNote):
    new_id = counter_manager.new_note_id()

    if not os.path.exists("notes"):
        os.makedirs("notes")

    note_path = f"notes/note{new_id}.json"

    note_data = {
        "text": note.text,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    with open(note_path, "w") as note_file:
        json.dump(note_data, note_file)

    counter_manager.save_counter()

    return model.CreateNoteResponse(id=new_id)


@app_router.patch("/notes/{note_id}", response_model=model.UpdateNoteTextResponse)
def create_note(note_id: int, note_updated: model.UpdateNoteText):
    note_data = get_note_data(note_id)
    note_data["text"] = note_updated.text

    note_path = f"notes/note{note_id}.json"
    with open(note_path, "w") as note_file:
        json.dump(note_data, note_file)

    return model.UpdateNoteTextResponse(id=note_id, text=note_data["text"], updated_at=datetime.now())


@app_router.get("/notes/{note_id}/info", response_model=model.GetNoteInfoResponse)
def get_info(note_id: int):
    note_data = get_note_data(note_id)

    return model.GetNoteInfoResponse(created_at=note_data["created_at"], updated_at=note_data["updated_at"])


@app_router.get("/notes/{note_id}/text", response_model=model.GetNoteTextResponse)
def get_text(note_id: int):
    note_data = get_note_data(note_id)

    return model.GetNoteTextResponse(id=note_data["id"], text=note_data["text"])
