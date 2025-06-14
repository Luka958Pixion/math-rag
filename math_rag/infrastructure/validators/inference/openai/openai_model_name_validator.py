from openai import models


class OpenAIModelNameValidator:
    @staticmethod
    def validate(model_name: str):
        for model in models.list():
            if model.id == model_name:
                return

        raise ValueError(f'Model {model_name} not found')
