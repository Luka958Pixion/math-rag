from pydantic import BaseModel
from requests import RequestException, post


class KatexValidationResult(BaseModel):
    valid: bool
    error: str | None = None


class KatexService:
    def validate(self, latex: str) -> KatexValidationResult:
        try:
            response = post(
                'http://localhost:3000/validate',
                data=latex.encode('utf-8'),
                headers={'Content-Type': 'text/plain'},
            )
            result = response.json()

            return KatexValidationResult(**result)

        except RequestException:
            raise

    def validate_many(self, latexes: list[str]) -> list[KatexValidationResult]:
        try:
            response = post(
                'http://localhost:3000/validate-many',
                json=latexes,  # json automatically encodes to utf-8
                headers={'Content-Type': 'application/json'},
            )
            results = response.json()

            return [KatexValidationResult(**result) for result in results]

        except RequestException:
            raise
