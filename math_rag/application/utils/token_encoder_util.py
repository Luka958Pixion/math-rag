import base64
import json


class TokenEncoderUtil:
    @staticmethod
    def encode(payload: dict) -> str:
        payload_json = json.dumps(payload)
        payload_json_bytes = payload_json.encode()

        return base64.urlsafe_b64encode(payload_json_bytes).decode()

    @staticmethod
    def decode(token: str) -> dict:
        payload_json = base64.urlsafe_b64decode(token).decode()

        return json.loads(payload_json)
