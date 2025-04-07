from pathlib import Path


class FileReaderUtil:
    @staticmethod
    def read(source: Path | bytes) -> str:
        for encoding in ('utf-8', 'latin1', 'cp1252'):
            try:
                if isinstance(source, Path):
                    with open(source, 'r', encoding=encoding) as file:
                        return file.read()

                elif isinstance(source, bytes):
                    return source.decode(encoding)

            except UnicodeDecodeError:
                continue
