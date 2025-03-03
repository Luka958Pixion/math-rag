from requests import RequestException, post


class KatexService:
    def validate(self, latex: str) -> bool:
        try:
            response = post(
                'http://localhost:3000/validate',
                data=latex.encode('utf-8'),
                headers={'Content-Type': 'text/plain'},
            )

            return response.json()

        except RequestException:
            raise

    def validate_many(self, latexes: list[str]) -> list[bool]:
        try:
            response = post(
                'http://localhost:3000/validate-many',
                json=latexes,  # json automatically encodes to utf-8
                headers={'Content-Type': 'application/json'},
            )

            return response.json()

        except RequestException:
            raise
