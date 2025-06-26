import importlib
import json

from enum import Enum
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from typing import TYPE_CHECKING, cast
from uuid import UUID

import huggingface_hub
import wandb

from accelerate import Accelerator
from accelerate.utils import DistributedDataParallelKwargs
from datasets import ClassLabel, DatasetDict, load_dataset
from datasets.download import DownloadConfig
from decouple import config
from fine_tune_settings import FineTuneSettings
from optuna import Trial
from outlines.generate.json import json as outlines_json
from outlines.models.transformers import Transformers
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from pydantic import BaseModel, create_model
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from stubs import ModelSpec
from torch import cuda
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


# huggingface
HF_HOME = Path('home')
HF_USERNAME = config('HF_USERNAME', default=None)
HF_TOKEN = config('HF_TOKEN', default=None)

# weights and biases
WANDB_PROJECT = config('WANDB_PROJECT', default=None)
WANDB_API_KEY = config('WANDB_API_KEY', default=None)

basicConfig(level=INFO, format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
logger = getLogger(__name__)

accelerator = Accelerator(
    kwargs_handlers=[DistributedDataParallelKwargs(find_unused_parameters=False)]
)
use_accelerator = accelerator.num_processes > 1

devices = [cuda.get_device_name(i) for i in range(cuda.device_count())]
logger.info(f'Running {len(devices)} devices: {devices}')


def import_model_spec(name: str) -> ModelSpec:
    module_name = name.split('/')[-1].lower().replace('-', '_').replace('.', '_')
    module = importlib.import_module(module_name)

    return cast(ModelSpec, module)


class GracefulStopCallback(TrainerCallback):
    def on_step_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ):
        return control


class LoRAWandbCallback(WandbCallback):
    def __init__(self, trial: Trial, settings: FineTuneSettings, fine_tune_job_id: UUID):
        super().__init__()
        self.trial = trial
        self.fine_tune_job_id = fine_tune_job_id

        self.r = trial.params[settings.optuna_settings.trial_settings.r.name]
        self.lora_alpha = trial.params[settings.optuna_settings.trial_settings.lora_alpha.name]
        self.lora_dropout = trial.params[settings.optuna_settings.trial_settings.lora_dropout.name]

    def on_train_begin(self, args, state, control, **kwargs):
        # avoid creating multiple runs
        if use_accelerator and not accelerator.is_main_process:
            return control

        if wandb.run is not None:
            wandb.finish()

        wandb.init(
            project=WANDB_PROJECT,
            name=f'fine-tune-job-{self.fine_tune_job_id}-trial-{self.trial.number}-run',
            config={
                'r': self.r,
                'lora_alpha': self.lora_alpha,
                'lora_dropout': self.lora_dropout,
            },
            tags=['lora', 'optuna'],
            settings=wandb.Settings(
                mode='shared',
                x_primary=True,
                # x_stats_gpu_device_ids=[accelerator.device.index],
            ),
        )

        return control

    def on_train_end(self, args, state, control, **kwargs):
        wandb.finish()


class Metric(Enum):
    ACCURACY = 'accuracy'
    PRECISION = 'precision'
    RECALL = 'recall'
    F1 = 'f1'


MODEL_NAMES = {'meta-llama/Llama-3.1-8B-Instruct'}
METRIC_NAMES = {name.value for name in Metric}


def fine_tune_and_evaluate(
    trial: Trial, settings: FineTuneSettings, fine_tune_job_id: UUID
) -> float:
    # validate
    model_name = settings.model_settings.model_name
    metric_name = settings.optuna_settings.metric_name

    if model_name not in MODEL_NAMES:
        raise ValueError(f'Model {model_name} is not available')

    if metric_name not in METRIC_NAMES:
        raise ValueError(f'Metric {metric_name} is not available')

    metric = Metric(metric_name)

    # load model specification
    model_spec = import_model_spec(model_name)

    # login
    huggingface_hub.login(token=HF_TOKEN)
    wandb.login(key=WANDB_API_KEY)

    # initialize tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=model_name,
        use_fast=True,
        trust_remote_code=True,
    )
    tokenizer = cast(PreTrainedTokenizerBase, tokenizer)
    model_spec.init_tokenizer(tokenizer)

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
    prompt_collection_json_bytes = Path(prompt_json_path).read_bytes()
    prompt_collection = cast(dict, json.loads(prompt_collection_json_bytes))

    # remove unwanted columns
    user_prompt = cast(dict, prompt_collection.get('user'))
    input_keys = cast(list[str], user_prompt.get('input_keys'))
    columns_to_keep = [*input_keys, 'label']
    columns_to_remove = {
        column
        for _, columns in dataset_dict.column_names.items()
        for column in columns
        if column not in columns_to_keep
    }
    dataset_dict = dataset_dict.remove_columns(list(columns_to_remove))

    original_validate_dataset = dataset_dict['validate']

    dataset_dict = dataset_dict.map(
        lambda x: model_spec.format_prompt(x, prompt_collection),
        remove_columns=dataset_dict['train'].column_names,
    )
    dataset_dict = dataset_dict.map(
        lambda batch: model_spec.formatting_func(tokenizer, {'messages': batch['messages']}),
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
        llm_int8_enable_fp32_cpu_offload=False,  # TODO try False
    )
    model = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=model_name,
        trust_remote_code=True,
        quantization_config=bits_and_bytes_config,
        # device_map='auto',    # NOTE: avoid torch DTensor error
        device_map={str(): accelerator.device} if use_accelerator else 'auto',
    )
    model = cast(PreTrainedModel, model)
    model_spec.init_language_model(model)
    model.resize_token_embeddings(len(tokenizer))
    model.config.pad_token_id = tokenizer.pad_token_id
    model.config.use_cache = False

    model = prepare_model_for_kbit_training(
        model=model,
        use_gradient_checkpointing=True,
    )
    model = cast(PreTrainedModel, model)
    model.gradient_checkpointing_enable(
        gradient_checkpointing_kwargs={'use_reentrant': False}
    )  # NOTE: avoid DDP error

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
    model = get_peft_model(
        model=model,
        peft_config=peft_config,
        adapter_name='default',
        mixed=False,
    )

    # fine-tune
    state_path = HF_HOME / f'fine-tune-job-{fine_tune_job_id}' / f'trial-{trial.number}' / 'state'
    model_path = HF_HOME / f'fine-tune-job-{fine_tune_job_id}' / f'trial-{trial.number}' / 'model'
    state_path.mkdir(parents=True, exist_ok=True)
    model_path.mkdir(parents=True, exist_ok=True)

    sft_config = SFTConfig(
        output_dir=state_path,
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
    lora_wandb_callback = LoRAWandbCallback(trial, settings, fine_tune_job_id)
    data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        data_collator=data_collator,
        train_dataset=train_dataset,
        eval_dataset=validate_dataset,
        processing_class=tokenizer,
        callbacks=[graceful_stop_callback, lora_wandb_callback],
        optimizer_cls_and_kwargs=(AdamW, settings.optimizer_settings.model_dump()),
    )
    last_checkpoint = get_last_checkpoint(sft_config.output_dir)

    trainer.train(
        resume_from_checkpoint=last_checkpoint,
        trial=trial,
        ignore_keys_for_eval=['past_key_values', 'hidden_states', 'attentions'],
    )
    trainer.model.save_pretrained(
        save_directory=model_path,
        push_to_hub=False,
        token=None,
        save_peft_format=True,
    )

    # evaluate
    class_label = cast(ClassLabel, original_validate_dataset.features['label'])

    if TYPE_CHECKING:

        class LabelEnum(str, Enum):
            pass

        class Label(BaseModel):
            label: LabelEnum

    else:
        LabelEnum = Enum('LabelEnum', {name: name for name in class_label.names}, type=str)
        Label = create_model('Label', label=(LabelEnum, ...))

    true_labels = [class_label.names[int(x['label'])] for x in original_validate_dataset]

    outlines_model = Transformers(model, tokenizer)
    sequence_generator_adapter = outlines_json(outlines_model, Label)
    predictions = []

    for sample in original_validate_dataset:
        messages = model_spec.format_prompt(sample, prompt_collection)['messages']
        input_token_ids = tokenizer.apply_chat_template(
            messages[:2],  # removes the assistant message (answer)
            tokenize=False,
            add_generation_prompt=False,
        )
        result: Label = sequence_generator_adapter(
            input_token_ids, max_tokens=settings.model_settings.max_tokens, stop_at='}'
        )
        predictions.append(result.label.value)

    match metric:
        case Metric.ACCURACY:
            return accuracy_score(true_labels, predictions)

        case Metric.PRECISION:
            return precision_score(true_labels, predictions, average='macro')

        case Metric.RECALL:
            return recall_score(true_labels, predictions, average='macro')

        case Metric.F1:
            return f1_score(true_labels, predictions, average='macro')
