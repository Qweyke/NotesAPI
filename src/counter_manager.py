import os


class CounterManager:
    def __init__(self, path):
        self.__file_path = path
        self.__counter = self.load_counter()

    def load_counter(self) -> int:
        if os.path.exists(self.__file_path):
            with open(self.__file_path, "r") as file:
                return int(file.read())
        else:
            return 0

    def save_counter(self):
        with open(self.__file_path, "w") as file:
            file.write(str(self.__counter))

    def new_note_id(self) -> int:
        self.__counter += 1
        return self.__counter

    def get_counter(self) -> int:
        return self.__counter
