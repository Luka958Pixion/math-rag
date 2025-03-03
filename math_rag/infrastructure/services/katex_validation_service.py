from pydantic import BaseModel
from requests import RequestException, post

from math_rag.application.models import KatexValidationResult


class KatexValidationService:
    def validate(self, katex: str) -> KatexValidationResult:
        try:
            response = post(
                'http://localhost:3000/validate',
                data=katex.encode('utf-8'),
                headers={'Content-Type': 'text/plain'},
            )
            result = response.json()

            return KatexValidationResult(**result)

        except RequestException:
            raise

    def validate_many(self, katexes: list[str]) -> list[KatexValidationResult]:
        try:
            response = post(
                'http://localhost:3000/validate-many',
                json=katexes,  # json automatically encodes to utf-8
                headers={'Content-Type': 'application/json'},
            )
            results = response.json()

            return [KatexValidationResult(**result) for result in results]

        except RequestException:
            raise
