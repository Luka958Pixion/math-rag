from pathlib import Path
from tarfile import open as tar_open


class TarFileExtractorUtil:
    @staticmethod
    def extract_tar_gz_to_path(source: Path, target: Path) -> None:
        target.mkdir(parents=True, exist_ok=True)
        mode = 'r:gz' if source.suffix == '.gz' else 'r'

        with tar_open(source, mode=mode) as tar_file:
            tar_file.extractall(path=target)
