from huggingface_hub import repo_exists


class HuggingFaceValidator:
    @staticmethod
    def validate_model_name(model_name: str):
        if repo_exists(model_name):
            return

        raise ValueError(f'Model {model_name} not found')
