from enum import Enum


class LLMResponseFormat(str, Enum):
    TEXT = 'text'
    JSON_OBJECT = 'json_object'
    JSON_SCHEMA = 'json_schema'
