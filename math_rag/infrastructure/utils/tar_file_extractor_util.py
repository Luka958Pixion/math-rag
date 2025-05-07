from pathlib import Path
from tarfile import open as tar_open


class TarFileExtractorUtil:
    @staticmethod
    def extract_tar_gz_to_path(source: Path, target: Path) -> None:
        target.mkdir(parents=True, exist_ok=True)

        with tar_open(source, mode='r:gz') as tar_file:
            tar_file.extractall(path=target)
