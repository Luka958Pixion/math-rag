from huggingface_hub import repo_exists


class HuggingFaceModelNameValidator:
    @staticmethod
    def validate(model_name: str):
        if repo_exists(model_name):
            return

        raise ValueError(f'Model {model_name} not found')
