from abc import ABC, abstractmethod
from pathlib import Path


class BaseLatexConverterClient(ABC):
    @abstractmethod
    def convert_image(self, *, file_path: Path | None, url: str | None) -> str:
        pass

    @abstractmethod
    def convert_pdf(self, *, file_path: Path | None, url: str | None) -> str:
        pass
