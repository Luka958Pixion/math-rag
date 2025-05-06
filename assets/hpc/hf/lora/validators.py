from pydantic import BaseModel


class GetPeftModelValidator(BaseModel):
    """
    Validator model for configuring `peft.get_peft_model` method.

    Reference:
        https://huggingface.co/docs/peft/v0.15.0/en/package_reference/peft_model#peft.get_peft_model

    Notes:
        - The `model` and `peft_config` parameters are not configurable.
    """

    adapter_name: str | None = 'default'
    mixed: bool | None = False
    autocast_adapter_dtype: bool | None = True
    revision: str | None = 'main'
    low_cpu_mem_usage: bool | None = False


class LoadDatasetValidator(BaseModel):
    pass
