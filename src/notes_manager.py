import json
import os
from datetime import datetime

import fastapi

PATH = "notes/manager.json"


class NotesManager:
    def __init__(self):

        if not os.path.exists("notes"):
            os.makedirs("notes")

        self.__file_path = PATH
        self.__notes = self.load_notes_list()

    @staticmethod
    def datetime_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError("Type not serializable for datetime")

    def load_notes_list(self) -> dict:
        if os.path.exists(self.__file_path):
            with open(self.__file_path, "r") as file:
                return json.load(file)
        else:
            return {}

    def __save_notes_list(self):
        with open(self.__file_path, "w") as file:
            json.dump(self.__notes, file)

    def add_note(self, note_id: int, text: str):

        if str(note_id) not in self.__notes:
            note_path = f"notes/note{note_id}.json"

            note_data = {
                "id": note_id,
                "text": text,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            with open(note_path, "w") as note_file:
                json.dump(note_data, note_file, default=self.datetime_serializer)

            self.__notes[str(note_id)] = note_path

            self.__save_notes_list()

        else:
            raise fastapi.HTTPException(status_code=400, detail=f"Note with ID:{note_id} already exists")

    def get_note_path(self, note_id: int) -> str:
        note_id_str = str(note_id)
        if note_id_str in self.__notes:
            return self.__notes[str(note_id)]
        else:
            raise fastapi.HTTPException(status_code=404, detail="Note not found")

    def get_note_data(self, note_id: int):
        note_path = self.get_note_path(note_id)

        with open(note_path, "r") as note_file:
            note_data = json.load(note_file)

        return note_data

    def update_note_data(self, note_id: int, note_data):
        note_path = self.get_note_path(note_id)

        with open(note_path, "w") as note_file:
            json.dump(note_data, note_file)

    def delete_note(self, note_id: int):
        note_id_str = str(note_id)
        if note_id_str in self.__notes:
            os.remove(self.get_note_path(note_id))
            del self.__notes[note_id_str]
            self.__save_notes_list()
        else:
            raise fastapi.HTTPException(status_code=404, detail="Note not found")

    def get_notes_list(self) -> dict:
        return {index: int(note_id) for index, note_id in enumerate(self.__notes.keys())}
