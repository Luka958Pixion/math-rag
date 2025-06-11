from pathlib import Path

from mpxpy.mathpix_client import MathpixClient as _MathpixClient

from math_rag.application.base.clients import BaseLatexConverterClient


ALLOWED_IMAGE_TYPES = {
    'jpeg',
    'jpg',
    'jpe',
    'png',
    'bmp',
    'dib',
    'jp2',
    'webp',
    'pbm',
    'pgm',
    'ppm',
    'pxm',
    'pnm',
    'pfm',
    'sr',
    'ras',
    'tiff',
    'tif',
    'exr',
    'hdr',
    'pic',
}
UPLOADS_PATH = Path(__file__).parents[3] / '.tmp' / 'mathpix' / 'uploads'  # TODO??
DOWNLOADS_PATH = Path(__file__).parents[3] / '.tmp' / 'mathpix' / 'downloads'


class MathpixClient(BaseLatexConverterClient):
    def __init__(self, client: _MathpixClient):
        self.client = client

    def convert_image(self, *, file_path: Path | None = None, url: str | None = None) -> str:
        image_type = file_path.suffix.removeprefix('.')

        if image_type not in ALLOWED_IMAGE_TYPES:
            raise ValueError(f'Image type {image_type} is not allowed')

        image = self.client.image_new(file_path=file_path, url=url)
        results = image.results()

        if 'text' not in results:
            raise ValueError(f'Results {results} do not contain text')

        return results['text']

    def convert_pdf(self, *, file_path: Path | None = None, url: str | None = None) -> str:
        pdf = self.client.pdf_new(
            file_path=file_path,
            url=url,
            convert_to_tex_zip=True,
        )
        pdf.wait_until_complete(timeout=60)
        content = pdf.to_tex_zip_bytes()
        # TODO

        with open(DOWNLOADS_PATH / 'data.zip', 'wb') as file:
            file.write(content)
