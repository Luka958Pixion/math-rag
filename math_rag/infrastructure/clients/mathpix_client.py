from mpxpy.mathpix_client import MathpixClient as _MathpixClient

from math_rag.application.base.clients import BaseMathpixClient


class MathpixClient(BaseMathpixClient):
    def __init__(self, client: _MathpixClient):
        self.client = client

    def process_image(self):
        image = self.client.image_new(file_path=..., url=...)

        # Get Mathpix Markdown (MMD)
        mmd = image.mmd()
        print(mmd)

        # Get line-by-line OCR data
        lines = image.lines_json()
        print(lines)

    def process_pdf(self):
        pdf = self.client.pdf_new(
            url='http://cs229.stanford.edu/notes2020spring/cs229-notes1.pdf',
            convert_to_tex_zip=True,
        )
        pdf.wait_until_complete(timeout=60)
        pdf.to_tex_zip_bytes()  # NOTE: this is latex + images
