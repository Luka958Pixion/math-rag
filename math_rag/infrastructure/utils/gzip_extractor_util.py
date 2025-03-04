from gzip import GzipFile
from io import BytesIO
from tarfile import open


class GzipExtractorUtil:
    @staticmethod
    def extract_gz(data: bytes) -> bytes:
        with GzipFile(fileobj=BytesIO(data)) as stream:
            return stream.read()

    @staticmethod
    def extract_tar_gz(data: bytes) -> dict[str, bytes]:
        result = {}

        with open(fileobj=BytesIO(data), mode='r:gz') as tar:
            for member in tar.getmembers():
                if not member.isfile():
                    continue

                extracted = tar.extractfile(member)

                if extracted:
                    result[member.name] = extracted.read()

        return result
