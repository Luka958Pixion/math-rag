import re


class StrUtil:
    @staticmethod
    def to_snake_case(text: str) -> str:
        # replace all runs of spaces or dashes with underscores
        text = re.sub(r'[\s\-]+', '_', text)

        # convert camel case to snake case: StrUtil -> Str_Util
        text = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', text)

        # handle acronym or lowercase to uppercase boundaries: OpenAI -> Open_AI
        text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)

        # lowercase
        return text.lower()
