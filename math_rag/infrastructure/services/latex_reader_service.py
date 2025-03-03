from pathlib import Path


class LatexReaderService:
    def read(self, file: Path | bytes) -> str:
        for encoding in ('utf-8', 'latin1', 'cp1252'):
            try:
                if isinstance(file, Path):
                    with open(file, 'r', encoding=encoding) as f:
                        return f.read()

                elif isinstance(file, bytes):
                    return file.decode(encoding)

            except UnicodeDecodeError:
                continue
