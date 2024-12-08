import sys
import threading
import time

import requests
from fastapi import FastAPI
from uvicorn import Config, Server

from src.router import app_router

app = FastAPI()
app.include_router(app_router)
HOST = "127.0.0.1"
PORT = 8080
URL = f"http://{HOST}:{PORT}"


class Client:

    def __init__(self, host: str, port: int, url: str):
        self.__host = host
        self.__port = port
        self.__url = url
        self.__jwt = None
        self.__server = None
        self.__status = 0
        self.__run_server()

    def __run_server(self):
        def init():
            config = Config(app=app, host=self.__host, port=self.__port, reload=True)
            self.__server = Server(config)
            self.__server.run()

        server_thread = threading.Thread(target=init, daemon=True)
        server_thread.start()
        time.sleep(1)

    def __show_info(self):
        if self.__status == 0:
            print("____________")
            print("1. Register")
            print("2. Authorize")
            print("q. Quit")
        elif self.__status == 1:
            print("__________________")
            print("1. Add note")
            print("2. Delete note")
            print("3. Update note")
            print("4. Get note text")
            print("5. Get note info")
            print("6. Get notes list")
            print("q. Quit")

    def power_client(self):
        print("NotesApi by Qweyke")
        self.__show_info()
        while True:
            choice = input()

            if choice == "1" and self.__status == 0:
                print("Registration")
                name = input("Enter desired username -> ")
                password = input(f"Enter desired password, {name} -> ")
                response = requests.post(url=f"{self.__url}/users/register", json={"name": name, "password": password})
                if response.ok:
                    print(f"You've registered successfully, {response.json().get("name")}!\n")
                else:
                    print(f"Something went wrong: HTTP{response.status_code}. {response.json().get("detail")}\n")

            elif choice == "2" and self.__status == 0:
                print("Authorization")
                name = input("Enter your username -> ")
                password = input(f"Enter your password, {name} -> ")
                response = requests.get(url=f"{self.__url}/users/authorize", json={"name": name, "password": password})
                if response.ok:
                    self.__jwt = response.json().get("token")
                    print(f"You've authorized successfully, {response.json().get("name")}!\n")
                    self.__status = 1

                else:
                    print(f"Something went wrong: HTTP{response.status_code}. {response.json().get("detail")}\n")

            elif choice == "1" and self.__status == 1:
                print("New note:")
                note_id = input("ID -> ")
                note_text = input(f"Text -> ")
                response = requests.post(url=f"{self.__url}/notes/new/{note_id}", json={"text": note_text},
                                         headers={"Authorization": f"Bearer {self.__jwt}"})
                if response.ok:
                    print(
                        f"Note with ID {response.json().get("id")} has been created successfully,"
                        f" {response.json().get("name")}!\n")
                else:
                    print(f"Something went wrong: HTTP{response.status_code}. {response.json().get("detail")}\n")

            elif choice == "2" and self.__status == 1:
                print("Delete note:")
                response_1 = requests.get(url=f"{self.__url}/notes/list",
                                          headers={"Authorization": f"Bearer {self.__jwt}"})
                print(response_1.json().get("notes_ids"))
                note_id = input("ID -> ")
                response = requests.delete(url=f"{self.__url}/notes/delete/{note_id}",
                                           headers={"Authorization": f"Bearer {self.__jwt}"})
                if response.ok:
                    print(
                        f"Note with ID {response.json().get("id")} has been deleted successfully,"
                        f" {response.json().get("name")}!\n")
                else:
                    print(f"Something went wrong: HTTP{response.status_code}. {response.json().get("detail")}\n")

            elif choice == "q":
                self.__shutdown()
            else:
                print("Wrong input")

            self.__show_info()

    def __shutdown(self):
        if self.__server and self.__server.should_exit is False:
            print("Shutting down the server...")
            self.__server.should_exit = True
            sys.exit(0)


if __name__ == "__main__":
    Client(HOST, PORT, URL).power_client()
