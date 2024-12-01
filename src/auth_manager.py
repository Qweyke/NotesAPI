import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import Request, HTTPException
from jose import jwt

KEY = "MyKey1337"
ALG = "HS256"

USERS_PATH = "../users.json"


class AuthorizationManager:

    def __init__(self):
        self.__file_path = USERS_PATH
        self.__secret = KEY
        self.__users = self.__load_users()

    def __load_users(self) -> Dict:
        if os.path.exists(self.__file_path):
            with open(self.__file_path, "r") as file:
                return json.load(file)
        else:
            return {}

    def __save_users(self):
        with open(self.__file_path, "w") as file:
            json.dump(self.__users, file)

    def register_user(self, name: str, password: str):
        if name in self.__users:
            raise HTTPException(status_code=409, detail="User already exists")
        self.__users[name] = {"password": password}
        self.__save_users()

    def generate_jwt(self, name: str, password: str) -> Optional[str]:
        user = self.__users.get(name)
        if user:
            if user["password"] == password:
                payload = {"iss": name, "exp": datetime.now() + timedelta(minutes=5)}
                try:
                    return jwt.encode(payload, self.__secret, ALG)
                except jwt.JWTError as ex:
                    raise HTTPException(status_code=500, detail=f"Something went wrong: {ex}")
            raise HTTPException(status_code=401, detail="Wrong password")
        raise HTTPException(status_code=404, detail="User not found")

    def verify_jwt(self, request: Request):
        try:
            token = request.headers.get("Authorization")
            token = token.replace('Bearer', '')
            payload = jwt.decode(token, self.__secret, ALG)
            user = self.__users.get(payload.get("iss"))
            if user:
                return True
            return False
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Expired token")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid or missing token")
