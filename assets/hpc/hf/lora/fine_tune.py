import json

from enum import Enum
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from typing import TYPE_CHECKING, cast
from uuid import UUID

import huggingface_hub
import wandb

from datasets import ClassLabel, DatasetDict, load_dataset
from datasets.download import DownloadConfig
from decouple import config
from fine_tune_settings import FineTuneSettings
from optuna import Trial
from outlines.generate.json import json as outlines_json
from outlines.models.transformers import Transformers
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from pydantic import BaseModel, create_model
from sklearn.metrics import f1_score
from torch.optim import AdamW
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling,
    PreTrainedModel,
    PreTrainedTokenizerBase,
    TrainerCallback,
    TrainerControl,
    TrainerState,
    TrainingArguments,
)
from transformers.integrations import WandbCallback
from transformers.trainer_utils import get_last_checkpoint
from trl import SFTConfig, SFTTrainer

from assets.hpc.hf.lora.llama_3_1_8b_instruct import (
    format_prompt,
    formatting_func,
    init_language_model,
    init_tokenizer,
)


# huggingface
HF_HOME = Path('home')
HF_USERNAME = config('HF_USERNAME', default=None)
HF_TOKEN = config('HF_TOKEN', default=None)

# weights and biases
WANDB_PROJECT = config('WANDB_PROJECT', default=None)
WANDB_API_KEY = config('WANDB_API_KEY', default=None)

# paths
TRAINER_STATE_PATH = HF_HOME / 'trainer' / 'state'
TRAINER_MODEL_PATH = HF_HOME / 'trainer' / 'model'

TRAINER_STATE_PATH.mkdir(parents=True, exist_ok=True)
TRAINER_MODEL_PATH.mkdir(parents=True, exist_ok=True)

SUPPORTED_MODEL_NAMES = {'meta-llama/Llama-3.1-8B-Instruct'}


basicConfig(level=INFO, format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
logger = getLogger(__name__)


class GracefulStopCallback(TrainerCallback):
    def on_step_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ):
        return control


class CustomWandbCallback(WandbCallback):
    def __init__(self, trial: Trial, settings: FineTuneSettings, fine_tune_job_id: UUID):
        super().__init__()
        self.trial = trial
        self.fine_tune_job_id = fine_tune_job_id

        self.r = trial.params[settings.optuna_settings.trial_settings.r.name]
        self.lora_alpha = trial.params[settings.optuna_settings.trial_settings.lora_alpha.name]
        self.lora_dropout = trial.params[settings.optuna_settings.trial_settings.lora_dropout.name]

    def on_train_begin(self, args, state, control, **kwargs):
        if wandb.run is not None:
            wandb.finish()

        wandb.init(
            project=WANDB_PROJECT,
            name=f'lora-optuna-job-{self.fine_tune_job_id}-trial-{self.trial.number}',
            config={
                'r': self.r,
                'lora_alpha': self.lora_alpha,
                'lora_dropout': self.lora_dropout,
            },
            tags=['lora', 'optuna', 'pretraining'],
        )

        return control

    def on_train_end(self, args, state, control, **kwargs):
        wandb.finish()


def fine_tune_and_evaluate(
    trial: Trial, settings: FineTuneSettings, fine_tune_job_id: UUID
) -> float:
    if settings.model_settings.model_name not in SUPPORTED_MODEL_NAMES:
        raise ValueError(f'Model {settings.model_settings.model_name} is not supported')

    # TODO dynamic imports based on model name

    # login
    huggingface_hub.login(token=HF_TOKEN)
    wandb.login(key=WANDB_API_KEY)

    # initialize tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=settings.model_settings.model_name,
        use_fast=True,
        trust_remote_code=True,
    )
    tokenizer = cast(PreTrainedTokenizerBase, tokenizer)
    init_tokenizer(tokenizer)

    # load dataset
    repo_id = f'{HF_USERNAME}/{settings.dataset_settings.dataset_name}'
    download_config = DownloadConfig(
        max_retries=3,
        disable_tqdm=True,
    )
    dataset_dict: DatasetDict = load_dataset(
        path=repo_id,
        name=settings.dataset_settings.config_name,
        split=None,
        download_config=download_config,
        token=HF_TOKEN,
        trust_remote_code=True,
    )
    prompt_json_path = huggingface_hub.hf_hub_download(
        repo_id=repo_id,
        filename='prompt.json',
        repo_type='dataset',
        token=HF_TOKEN,
    )
    prompt_json_bytes = Path(prompt_json_path).read_bytes()
    prompt = json.loads(prompt_json_bytes)

    original_train_dataset = dataset_dict['test']

    dataset_dict = dataset_dict.map(
        lambda x: format_prompt(x, prompt), remove_columns=dataset_dict['train'].column_names
    )
    dataset_dict = dataset_dict.map(
        lambda batch: formatting_func(tokenizer, {'messages': batch['messages']}),
        batched=True,
        batch_size=settings.sft_settings.per_device_train_batch_size,
        remove_columns=['messages'],
    )

    train_dataset = dataset_dict['train']
    validate_dataset = dataset_dict['validate']
    # test_dataset = dataset_dict['test']

    # initialize model
    bits_and_bytes_config = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_threshold=6.0,
        llm_int8_enable_fp32_cpu_offload=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=settings.model_settings.model_name,
        trust_remote_code=True,
        quantization_config=bits_and_bytes_config,
        device_map='auto',
    )
    model = cast(PreTrainedModel, model)
    init_language_model(model)
    model.resize_token_embeddings(len(tokenizer))
    model.config.pad_token_id = tokenizer.pad_token_id

    r = trial.params[settings.optuna_settings.trial_settings.r.name]
    lora_alpha = trial.params[settings.optuna_settings.trial_settings.lora_alpha.name]
    lora_dropout = trial.params[settings.optuna_settings.trial_settings.lora_dropout.name]

    peft_config = LoraConfig(
        r=r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        target_modules=settings.model_settings.target_modules,
        use_dora=True,
    )

    model = prepare_model_for_kbit_training(
        model=model,
        use_gradient_checkpointing=True,
    )

    model = get_peft_model(
        model=model,
        peft_config=peft_config,
        adapter_name='default',
        mixed=False,
    )

    # fine-tune
    sft_config = SFTConfig(
        output_dir=f'{TRAINER_STATE_PATH}/trial/{trial._trial_id}',
        do_train=True,
        do_eval=False,
        do_predict=False,
        per_device_eval_batch_size=2,
        eval_accumulation_steps=4,
        save_strategy='steps',
        save_steps=100,
        save_total_limit=2,
        disable_tqdm=True,
        per_device_train_batch_size=settings.sft_settings.per_device_train_batch_size,
        gradient_accumulation_steps=settings.sft_settings.gradient_accumulation_steps,
        learning_rate=settings.sft_settings.learning_rate,
        num_train_epochs=settings.sft_settings.num_train_epochs,
        fp16=settings.sft_settings.fp16,
        weight_decay=settings.sft_settings.weight_decay,
        report_to='none',
        logging_strategy='steps',
        logging_steps=100,
        logging_first_step=True,
        label_names=['labels'],
        remove_unused_columns=True,
    )

    graceful_stop_callback = GracefulStopCallback()
    custom_wandb_callback = CustomWandbCallback(trial, settings, fine_tune_job_id)
    data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        data_collator=data_collator,
        train_dataset=train_dataset,
        eval_dataset=validate_dataset,
        processing_class=tokenizer,
        callbacks=[graceful_stop_callback, custom_wandb_callback],
        optimizer_cls_and_kwargs=(AdamW, settings.optimizer_settings.model_dump()),
    )
    last_checkpoint = get_last_checkpoint(sft_config.output_dir)

    trainer.train(
        resume_from_checkpoint=last_checkpoint,
        trial=trial,
        ignore_keys_for_eval=['past_key_values', 'hidden_states', 'attentions'],
    )
    trainer.model.save_pretrained(
        save_directory=f'{TRAINER_MODEL_PATH}/trial/{trial._trial_id}',
        push_to_hub=False,
        token=None,
        save_peft_format=True,
    )

    class_label = cast(ClassLabel, original_train_dataset.features['label'])

    if TYPE_CHECKING:

        class LabelEnum(str, Enum):
            pass

        class Label(BaseModel):
            label: LabelEnum

    else:
        LabelEnum = Enum('LabelEnum', {name: name for name in class_label.names}, type=str)
        Label = create_model('Label', label=(LabelEnum, ...))

    outlines_model = Transformers(model, tokenizer)
    json_gen = outlines_json(outlines_model, Label)
    predictions = []
    true_labels = [class_label.names[int(x['label'])] for x in original_train_dataset]

    for sample in original_train_dataset:
        messages = format_prompt(sample, prompt)['messages']
        prompt_str = tokenizer.apply_chat_template(
            [
                {'role': 'system', 'content': messages[0]['content']},
                {'role': 'user', 'content': messages[1]['content']},
            ],
            tokenize=False,
            add_generation_prompt=False,
        )
        result: Label = json_gen(prompt_str, max_tokens=20, stop_at='}')
        predictions.append(result.label.value)

    return f1_score(true_labels, predictions, average='macro')
