import json
import os
from datetime import datetime, timedelta
from typing import Optional

import fastapi
import jwt
from fastapi import HTTPException

MANAGER_PATH = "../server/user_manager.json"
NOTES_PATH = "../server/notes"

KEY = "MyKey1337"
ALG = "HS256"


class Server:
    def __init__(self):

        if not os.path.exists(NOTES_PATH):
            os.makedirs(NOTES_PATH)

        self.__manager_path = MANAGER_PATH
        self.__manager_list = self.__load_manager_list()
        self.__algorithm = ALG
        self.__secret_key = KEY

    def __load_manager_list(self) -> dict:
        if os.path.exists(self.__manager_path):
            with open(self.__manager_path, "r") as file:
                return json.load(file)
        else:
            return {}

    def __save_manager_list(self):
        with open(self.__manager_path, "w") as file:
            json.dump(self.__manager_list, file)

    def generate_jwt(self, name: str, password: str) -> Optional[str]:
        user = self.__manager_list.get(name)
        if user:
            if user["password"] == password:
                payload = {"iss": name, "exp": datetime.now() + timedelta(minutes=35)}
                try:
                    return jwt.encode(payload, KEY, ALG)
                except jwt.PyJWTError as ex:
                    raise HTTPException(
                        status_code=500, detail=f"Something went wrong: {ex}"
                    )
            raise HTTPException(status_code=401, detail="Wrong password")
        raise HTTPException(status_code=404, detail="User not found")

    def __verify_jwt(self, bearer_token: str):
        try:
            token = bearer_token.replace("Bearer", "").strip()
            payload = jwt.decode(token, KEY, ALG)
            user = self.__manager_list.get(payload.get("iss"))
            if user is not None:
                return user
            raise HTTPException(status_code=404, detail="User not found")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Expired token")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid or missing token")

    @staticmethod
    def __datetime_serializer(obj) -> str:
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError("Type not serializable for datetime")

    def __get_note_path(self, token: str, note_id: int) -> str:
        user = self.__verify_jwt(token)
        note_path = f"{NOTES_PATH}/{user}/{note_id}.json"
        if os.path.isfile(note_path):
            return note_path
        raise fastapi.HTTPException(status_code=404, detail="Note not found")

    def register_user(self, name: str, password: str):
        if name in self.__manager_list:
            raise HTTPException(status_code=409, detail="User already exists")
        self.__manager_list[name] = {"password": password, "notes": []}
        self.__save_manager_list()
        if not os.path.exists(NOTES_PATH):
            os.makedirs(NOTES_PATH)

    def add_note(self, token: str, note_id: int, text: str):
        user = self.__verify_jwt(token)
        if str(note_id) not in self.__manager_list.get(user, {}).get("notes", []):
            note_data = {
                "id": note_id,
                "text": text,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }

            note_path = f"{NOTES_PATH}/{user}/{note_id}.json"
            with open(note_path, "w") as note_file:
                json.dump(note_data, note_file, default=self.__datetime_serializer)
            self.__save_manager_list()

        raise fastapi.HTTPException(
            status_code=400, detail=f"Note with ID:{note_id} already exists"
        )

    def get_note_data(self, token: str, note_id: int) -> dict:
        note_path = self.__get_note_path(token, note_id)

        with open(note_path, "r") as note_file:
            note_data = json.load(note_file)

        return note_data

    def update_note_data(self, token: str, note_id: int, text: str) -> dict:
        note_path = self.__get_note_path(token, note_id)
        note_data = self.get_note_data(token, note_id)
        note_data["text"] = text
        note_data["updated_at"] = datetime.now()
        with open(note_path, "w") as note_file:
            json.dump(note_data, note_file, default=self.__datetime_serializer)

        return note_data

    def delete_note(self, token: str, note_id: int) -> str:
        note_path = self.__get_note_path(token, note_id)
        os.remove(note_path)

        user = self.__verify_jwt(token)
        if str(note_id) in self.__manager_list[user]["notes"]:
            self.__manager_list[user]["notes"].remove(str(note_id))
        else:
            raise HTTPException(
                status_code=404, detail="Note ID not found in user's notes"
            )

        self.__save_manager_list()
        return self.__datetime_serializer(datetime.now())

    def get_notes_list(self, token: str) -> dict:
        user = self.__verify_jwt(token)
        notes_dict = {}
        for index, note_id in enumerate(self.__manager_list[user]["notes"]):
            notes_dict[index] = note_id
        return notes_dict