from string import Formatter

from pydantic import BaseModel, Field, model_validator


class LLMPrompt(BaseModel):
    template: str
    input_keys: list[str] = Field(default_factory=list)

    @model_validator(mode='before')
    @classmethod
    def extract_input_keys(cls, values: dict):
        formatter = Formatter()

        if 'input_keys' not in values or not values['input_keys']:
            template = values.get('template', '')
            field_names = {
                field_name for _, field_name, _, _ in formatter.parse(template) if field_name
            }
            values['input_keys'] = sorted(field_names)

        return values

    def format(self, **kwargs) -> str:
        missing_keys = set(self.input_keys) - kwargs.keys()

        if missing_keys:
            raise ValueError(f'Missing keys for prompt: {missing_keys}')

        return self.template.format(**kwargs)
