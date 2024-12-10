import json
import os
from datetime import datetime, timedelta
from typing import Optional

import fastapi
import jwt
from fastapi import HTTPException

MANAGER_PATH = "/server/user_manager.json"
NOTES_PATH = "/server/notes"

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

    def __verify_jwt(self, bearer_token: str) -> str:
        try:
            token = bearer_token.replace("Bearer", "").strip()
            payload = jwt.decode(token, KEY, ALG)
            user = payload.get("iss")
            if user is not None:
                return user
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as ex:
            raise HTTPException(status_code=401, detail=f"Invalid token: {ex}")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Expired token")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid or missing token")

    def __get_user_dict(self, bearer_token: str):
        user_dict = self.__manager_list.get(self.__verify_jwt(bearer_token))
        if user_dict is not None:
            return user_dict
        raise HTTPException(status_code=404, detail="User not found")

    @staticmethod
    def __datetime_serializer(obj) -> str:
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError("Type not serializable for datetime")

    def __get_note_path(self, bearer_token: str, note_id: int) -> str:
        user_name = self.__verify_jwt(bearer_token)

        note_path = f"{NOTES_PATH}/{user_name}/{note_id}.json"
        if (
                os.path.isfile(note_path)
                and str(note_id) in self.__manager_list[user_name]["notes"]
        ):
            return note_path
        raise fastapi.HTTPException(status_code=404, detail="Note not found")

    def register_user(self, name: str, password: str):
        if name in self.__manager_list:
            raise HTTPException(status_code=409, detail="User already exists")
        self.__manager_list[name] = {"password": password, "notes": []}
        self.__save_manager_list()
        if os.path.exists(NOTES_PATH):
            os.makedirs(f"{NOTES_PATH}/{name}")

    def add_note(self, bearer_token: str, note_id: int, text: str) -> Optional[str]:

        notes_list = self.__get_user_dict(bearer_token).get("notes")
        if str(note_id) not in notes_list:
            note_data = {
                "id": note_id,
                "text": text,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }

            user_name = self.__verify_jwt(bearer_token)
            note_path = f"{NOTES_PATH}/{user_name}/{note_id}.json"
            with open(note_path, "w") as note_file:
                json.dump(note_data, note_file, default=self.__datetime_serializer)

            self.__manager_list[user_name]["notes"].append(str(note_id))
            self.__save_manager_list()
            return user_name

        else:
            raise fastapi.HTTPException(
                status_code=400, detail=f"Note with ID:{note_id} already exists"
            )

    def get_note_data(self, token: str, note_id: int) -> dict:
        note_path = self.__get_note_path(token, note_id)

        with open(note_path, "r") as note_file:
            note_data = json.load(note_file)

        return note_data

    def update_note_data(self, token: str, note_id: int, text: str) -> str:
        note_path = self.__get_note_path(token, note_id)
        note_data = self.get_note_data(token, note_id)
        note_data["text"] = text
        note_data["updated_at"] = datetime.now()
        with open(note_path, "w") as note_file:
            json.dump(note_data, note_file, default=self.__datetime_serializer)

        return self.__verify_jwt(token)

    def delete_note(self, token: str, note_id: int) -> str:
        note_path = self.__get_note_path(token, note_id)
        os.remove(note_path)

        user_name = self.__verify_jwt(token)
        if str(note_id) in self.__manager_list[user_name]["notes"]:
            self.__manager_list[user_name]["notes"].remove(str(note_id))
        else:
            raise HTTPException(
                status_code=404, detail="Note ID not found in user's notes"
            )

        self.__save_manager_list()
        return user_name

    def get_notes_list(self, token: str) -> dict:
        user = self.__verify_jwt(token)
        notes_dict = {}
        for index, note_id in enumerate(self.__manager_list[user]["notes"]):
            notes_dict[index] = note_id
        return notes_dict
