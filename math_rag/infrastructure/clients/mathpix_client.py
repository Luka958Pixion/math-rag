from pathlib import Path

from mpxpy.mathpix_client import MathpixClient as _MathpixClient

from math_rag.application.base.clients import BaseLatexConverterClient


IMAGE_TYPES = (
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
)
CONTENT_TYPES = tuple('image/' + extension for extension in IMAGE_TYPES) + ('application/pdf',)


class MathpixClient(BaseLatexConverterClient):
    def __init__(self, client: _MathpixClient):
        self.client = client

    def convert_image(self, *, file_path: Path | None = None, url: str | None = None) -> str:
        if file_path:
            image_type = file_path.suffix.removeprefix('.')

            if image_type not in IMAGE_TYPES:
                raise ValueError(f'Image type {image_type} is not allowed')

        image = self.client.image_new(file_path=file_path, url=url)
        results = image.results()

        if 'error' in results:
            raise ValueError(results['error'])

        if 'text' not in results:
            raise ValueError(f'Results {results} do not contain text')

        return results['text']

    def convert_pdf(self, *, file_path: Path | None = None, url: str | None = None) -> bytes:
        pdf = self.client.pdf_new(
            file_path=file_path,
            url=url,
            convert_to_tex_zip=True,
        )
        pdf.wait_until_complete(timeout=60)

        return pdf.to_tex_zip_bytes()

    def list_content_types(self) -> list[str]:
        return list(CONTENT_TYPES)

    def list_image_types(self) -> list[str]:
        return list(IMAGE_TYPES)
