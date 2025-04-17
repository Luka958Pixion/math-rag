from hashlib import new
from pathlib import Path


class FileHasherUtil:
    @staticmethod
    def hash(file_path: Path, hash_function_name: str) -> str:
        with open(file_path, 'rb') as file:
            file_bytes = file.read()

        return new(hash_function_name, file_bytes).hexdigest()
