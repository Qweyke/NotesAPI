from datetime import datetime
import fastapi
import model

app_router = fastapi.APIRouter()
notes_db = {}


@app_router.post("/notes", response_model=model.CreateNoteResponse)
def create_note(note: model.CreateNoteResponse):
    new_id = len(notes_db) + 1
    notes_db[new_id] = {
        "text": note.text,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    return model.CreateNoteResponse(id=new_id)
