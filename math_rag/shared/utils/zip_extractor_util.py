from io import BytesIO
from pathlib import Path
from zipfile import ZipFile


class ZipExtractorUtil:
    @staticmethod
    def extract(source: bytes | Path, target: Path) -> bytes:
        source = BytesIO(source) if isinstance(source, bytes) else source

        with ZipFile(source, 'r') as file:
            file.extractall(target)
