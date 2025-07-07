import importlib
import json
import warnings

from argparse import ArgumentParser, ArgumentTypeError, Namespace
from contextlib import nullcontext
from enum import Enum
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING, cast
from uuid import UUID

import huggingface_hub
import torch
import wandb

from accelerate import Accelerator
from accelerate.utils import DistributedDataParallelKwargs
from datasets import ClassLabel, Dataset, DatasetDict, load_dataset
from datasets.download import DownloadConfig
from decouple import config
from fine_tune_settings import FineTuneSettings, OptunaTrialSettings
from optuna import Trial, load_study
from outlines.generate.api import SequenceGeneratorAdapter
from outlines.generate.json import json as outlines_json
from outlines.models.transformers import Transformers
from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training
from pydantic import BaseModel, create_model
from results import Result, TestResult, TrialResult
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from stubs import ModelSpec
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
from utils import JSONReaderUtil, JSONWriterUtil


DEBUG = False

# huggingface
HF_HOME = Path('home')
HF_USERNAME = config('HF_USERNAME', default=None)
HF_TOKEN = config('HF_TOKEN', default=None)

# weights and biases
WANDB_PROJECT = config('WANDB_PROJECT', default=None)
WANDB_API_KEY = config('WANDB_API_KEY', default=None)

basicConfig(level=INFO, format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
logger = getLogger(__name__)

warnings.filterwarnings(
    'ignore', message=r'MatMul8bitLt: inputs will be cast from .* to float16 during quantization'
)


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
    def __init__(
        self,
        trial: Trial,
        optuna_trial_settings: OptunaTrialSettings,
        fine_tune_job_id: UUID,
        gpu_indexes: list[int],
        accelerator: Accelerator | None,
    ):
        super().__init__()
        self.trial = trial
        self.fine_tune_job_id = fine_tune_job_id
        self.gpu_indexes = gpu_indexes
        self.accelerator = accelerator

        self.r = trial.params[optuna_trial_settings.r.name]
        self.lora_alpha = trial.params[optuna_trial_settings.lora_alpha.name]
        self.lora_dropout = trial.params[optuna_trial_settings.lora_dropout.name]

    def on_train_begin(self, args, state, control, **kwargs):
        if self.accelerator and not self.accelerator.is_main_process:
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
                x_stats_gpu_device_ids=self.gpu_indexes,
            ),
        )

        return control

    def on_train_end(self, args, state, control, **kwargs):
        if self.accelerator and not self.accelerator.is_main_process:
            return control

        wandb.finish()


class Metric(Enum):
    ACCURACY = 'accuracy'
    PRECISION = 'precision'
    RECALL = 'recall'
    F1 = 'f1'


MODEL_NAMES = {'meta-llama/Llama-3.1-8B-Instruct'}
METRIC_NAMES = {name.value for name in Metric}


def subset_dataset_splits(
    dataset_dict: DatasetDict, split_name_to_size: dict[str, int]
) -> DatasetDict:
    return DatasetDict(
        {
            split_name: dataset_dict[split_name].select(
                range(min(len(dataset_dict[split_name]), split_name_to_size[split_name]))
            )
            for split_name in dataset_dict
        }
    )


def train(
    accelerator: Accelerator | None,
    fine_tune_job_id: UUID,
    fine_tune_settings: FineTuneSettings,
    gpu_indexes: list[int],
    model_spec: ModelSpec,
    trial: Trial,
) -> tuple[PeftModel, PreTrainedTokenizerBase, dict, Dataset, Dataset, float]:
    model_name = fine_tune_settings.model_settings.model_name

    # initialize tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=model_name,
        use_fast=True,
        trust_remote_code=True,
    )
    tokenizer = cast(PreTrainedTokenizerBase, tokenizer)
    model_spec.init_tokenizer(tokenizer)

    # load dataset
    repo_id = f'{HF_USERNAME}/{fine_tune_settings.dataset_settings.dataset_name}'
    download_config = DownloadConfig(
        max_retries=3,
        disable_tqdm=True,
    )
    dataset_dict: DatasetDict = load_dataset(
        path=repo_id,
        name=fine_tune_settings.dataset_settings.config_name,
        split=None,
        download_config=download_config,
        token=HF_TOKEN,
        trust_remote_code=True,
    )

    if DEBUG:
        dataset_dict = subset_dataset_splits(dataset_dict, dict(train=100, validate=1111, test=100))

    download_kwargs = dict(
        repo_id=repo_id,
        filename='prompt.json',
        repo_type='dataset',
        token=HF_TOKEN,
    )

    with accelerator.main_process_first() if accelerator else nullcontext():
        prompt_json_path = huggingface_hub.hf_hub_download(**download_kwargs)

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

    validate_dataset = dataset_dict['validate']
    test_dataset = dataset_dict['test']

    dataset_dict = dataset_dict.map(
        lambda x: model_spec.format_prompt(x, prompt_collection),
        remove_columns=dataset_dict['train'].column_names,
    )
    dataset_dict = dataset_dict.map(
        lambda batch: model_spec.formatting_func(tokenizer, {'messages': batch['messages']}),
        batched=True,
        batch_size=fine_tune_settings.sft_settings.per_device_train_batch_size,
        remove_columns=['messages'],
    )

    train_dataset = dataset_dict['train']

    # initialize model
    bits_and_bytes_config = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_threshold=6.0,
        llm_int8_enable_fp32_cpu_offload=False,
    )
    model = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=model_name,
        trust_remote_code=True,
        quantization_config=bits_and_bytes_config,
        # NOTE: avoid torch DTensor error
        device_map={str(): accelerator.device} if accelerator else 'auto',
        # attn_implementation='flash_attention_2',
    )
    model = cast(PreTrainedModel, model)
    model_spec.init_language_model(model)
    model.resize_token_embeddings(len(tokenizer))
    model.config.pad_token_id = tokenizer.pad_token_id

    model = prepare_model_for_kbit_training(
        model=model,
        use_gradient_checkpointing=True,
    )
    model = cast(PreTrainedModel, model)
    # NOTE: use_cache can not be used with gradient_checkpointing
    model.config.use_cache = False
    # NOTE: avoid DDP error
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})

    trial_settings = fine_tune_settings.optuna_settings.trial_settings
    r = trial.params[trial_settings.r.name]
    lora_alpha = trial.params[trial_settings.lora_alpha.name]
    lora_dropout = trial.params[trial_settings.lora_dropout.name]

    peft_config = LoraConfig(
        r=r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        target_modules=fine_tune_settings.model_settings.target_modules,
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
        save_steps=500,
        save_total_limit=2,
        disable_tqdm=True,
        per_device_train_batch_size=fine_tune_settings.sft_settings.per_device_train_batch_size,
        gradient_accumulation_steps=fine_tune_settings.sft_settings.gradient_accumulation_steps,
        learning_rate=fine_tune_settings.sft_settings.learning_rate,
        num_train_epochs=fine_tune_settings.sft_settings.num_train_epochs,
        fp16=fine_tune_settings.sft_settings.fp16,
        weight_decay=fine_tune_settings.sft_settings.weight_decay,
        report_to='none',
        logging_strategy='steps',
        logging_steps=100,
        logging_first_step=True,
        label_names=['labels'],
        remove_unused_columns=True,
        ddp_find_unused_parameters=False,
        use_liger_kernel=True,
        dataloader_pin_memory=True,
    )
    graceful_stop_callback = GracefulStopCallback()
    lora_wandb_callback = LoRAWandbCallback(
        trial,
        fine_tune_settings.optuna_settings.trial_settings,
        fine_tune_job_id,
        gpu_indexes,
        accelerator,
    )
    data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        data_collator=data_collator,
        train_dataset=train_dataset,
        processing_class=tokenizer,
        callbacks=[graceful_stop_callback, lora_wandb_callback],
        optimizer_cls_and_kwargs=(
            torch.optim.AdamW,
            fine_tune_settings.optimizer_settings.model_dump(),
        ),
    )
    last_checkpoint = get_last_checkpoint(sft_config.output_dir)

    train_start = perf_counter()
    trainer.train(
        resume_from_checkpoint=last_checkpoint,
        trial=trial,
        ignore_keys_for_eval=['past_key_values', 'hidden_states', 'attentions'],
    )
    local_train_duration = perf_counter() - train_start

    if accelerator:
        # make a 1-element tensor and all-gather it across ranks
        tensor = torch.tensor(local_train_duration, device=accelerator.device)
        locals = accelerator.gather(tensor)
        # every rank picks the max
        train_duration = locals.max().item()

    else:
        train_duration = local_train_duration

    if accelerator:
        accelerator.wait_for_everyone()

    if accelerator is None or accelerator.is_main_process:
        trainer.model = cast(PeftModel, trainer.model)
        trainer.model.save_pretrained(
            save_directory=model_path,
            push_to_hub=False,
            token=None,
            save_peft_format=True,
            save_embedding_layers=True,
        )

    return model, tokenizer, prompt_collection, validate_dataset, test_dataset, train_duration


def validate(
    accelerator: Accelerator | None,
    fine_tune_settings: FineTuneSettings,
    metric: Metric,
    model: PeftModel,
    model_spec: ModelSpec,
    tokenizer: PreTrainedTokenizerBase,
    prompt_collection: dict,
    validate_dataset: Dataset,
) -> tuple[float, float, SequenceGeneratorAdapter]:
    class_label = cast(ClassLabel, validate_dataset.features['label'])

    if TYPE_CHECKING:

        class LabelEnum(str, Enum):
            pass

        class Label(BaseModel):
            label: LabelEnum

    else:
        LabelEnum = Enum('LabelEnum', {name: name for name in class_label.names}, type=str)
        Label = create_model('Label', label=(LabelEnum, ...))

    true_labels = [class_label.names[int(x['label'])] for x in validate_dataset]

    if accelerator:
        validate_dataset = validate_dataset.shard(
            num_shards=accelerator.num_processes,
            index=accelerator.process_index,
            contiguous=True,
        )

    # prepare model for inference
    device = accelerator.device if accelerator else torch.device('cuda')
    model.to(device)
    model.eval()
    model.config.use_cache = True

    outlines_model = Transformers(model, tokenizer)
    sequence_generator_adapter = outlines_json(outlines_model, Label)

    predictions_shard = []
    validate_start = perf_counter()

    with torch.no_grad():
        for sample in validate_dataset:
            messages = model_spec.format_prompt(sample, prompt_collection)['messages']
            input_token_ids = tokenizer.apply_chat_template(
                # NOTE: removes the assistant message (answer)
                messages[:2],
                tokenize=False,
                add_generation_prompt=False,
            )
            result: Label = sequence_generator_adapter(
                input_token_ids,
                max_tokens=fine_tune_settings.model_settings.max_tokens,
                stop_at='}',
            )
            predictions_shard.append(result.label.value)

    if accelerator:
        all_preds_per_rank: list[list[str]] = [None] * accelerator.num_processes
        torch.distributed.all_gather_object(all_preds_per_rank, predictions_shard)
        predictions = [label for shard in all_preds_per_rank for label in shard]

    else:
        predictions = predictions_shard

    local_validate_duration = perf_counter() - validate_start

    if accelerator:
        # make a 1-element tensor and all-gather it across ranks
        tensor = torch.tensor(local_validate_duration, device=accelerator.device)
        locals = accelerator.gather(tensor)
        # every rank picks the max
        validate_duration = locals.max().item()

    else:
        validate_duration = local_validate_duration

    match metric:
        case Metric.ACCURACY:
            score = accuracy_score(true_labels, predictions)

        case Metric.PRECISION:
            score = precision_score(true_labels, predictions, average='macro')

        case Metric.RECALL:
            score = recall_score(true_labels, predictions, average='macro')

        case Metric.F1:
            score = f1_score(true_labels, predictions, average='macro')

        case _:
            raise ValueError()

    return score, validate_duration, sequence_generator_adapter


def test(
    accelerator: Accelerator | None,
    fine_tune_settings: FineTuneSettings,
    sequence_generator_adapter: SequenceGeneratorAdapter,
    model_spec: ModelSpec,
    tokenizer: PreTrainedTokenizerBase,
    prompt_collection: dict,
    test_dataset: Dataset,
) -> TestResult:
    class_label = cast(ClassLabel, test_dataset.features['label'])

    if TYPE_CHECKING:

        class LabelEnum(str, Enum):
            pass

        class Label(BaseModel):
            label: LabelEnum

    else:
        LabelEnum = Enum('LabelEnum', {name: name for name in class_label.names}, type=str)
        Label = create_model('Label', label=(LabelEnum, ...))

    true_labels = [class_label.names[int(x['label'])] for x in test_dataset]

    if accelerator:
        test_dataset = test_dataset.shard(
            num_shards=accelerator.num_processes,
            index=accelerator.process_index,
            contiguous=True,
        )

    predictions_shard = []
    test_start = perf_counter()

    with torch.no_grad():
        for sample in test_dataset:
            messages = model_spec.format_prompt(sample, prompt_collection)['messages']
            input_token_ids = tokenizer.apply_chat_template(
                # NOTE: removes the assistant message (answer)
                messages[:2],
                tokenize=False,
                add_generation_prompt=False,
            )
            result: Label = sequence_generator_adapter(
                input_token_ids,
                max_tokens=fine_tune_settings.model_settings.max_tokens,
                stop_at='}',
            )
            predictions_shard.append(result.label.value)

    if accelerator:
        all_preds_per_rank: list[list[str]] = [None] * accelerator.num_processes
        torch.distributed.all_gather_object(all_preds_per_rank, predictions_shard)
        predictions = [label for shard in all_preds_per_rank for label in shard]

    else:
        predictions = predictions_shard

    local_test_duration = perf_counter() - test_start

    if accelerator:
        # make a 1-element tensor and all-gather it across ranks
        tensor = torch.tensor(local_test_duration, device=accelerator.device)
        locals = accelerator.gather(tensor)
        # every rank picks the max
        test_duration = locals.max().item()

    else:
        test_duration = local_test_duration

    # metrics
    accuracy = accuracy_score(true_labels, predictions)
    precision = precision_score(true_labels, predictions, average='macro')
    recall = recall_score(true_labels, predictions, average='macro')
    f1 = f1_score(true_labels, predictions, average='macro')

    # additional metrics
    balanced_accuracy = balanced_accuracy_score(true_labels, predictions)

    label_names = [name for name in class_label.names]
    report = classification_report(
        true_labels,
        predictions,
        labels=label_names,
        target_names=label_names,
        zero_division=0,
    )
    matrix = confusion_matrix(
        true_labels,
        predictions,
        labels=label_names,
    )

    return TestResult(
        metric_to_score=dict(
            accuracy=float(accuracy),
            precision=float(precision),
            recall=float(recall),
            f1=float(f1),
            balanced_accuracy=float(balanced_accuracy),
            report=str(report),
            matrix=matrix.tolist(),
        ),
        test_duration=test_duration,
    )


def parse_gpu_indexes(value: str) -> list[int]:
    try:
        return [int(i.strip()) for i in value.split(',')]

    except ValueError:
        raise ArgumentTypeError('GPU indexes must be comma-separated integers')


class Args(Namespace):
    fine_tune_job_id: UUID
    fine_tune_settings_path: Path
    fine_tune_result_path: Path
    trial_number: int
    gpu_indexes: list[int]
    use_accelerate: bool


def parse_args() -> Args:
    parser = ArgumentParser()
    parser.add_argument('--fine_tune_job_id', type=UUID, required=True)
    parser.add_argument('--fine_tune_settings_path', type=Path, required=True)
    parser.add_argument('--fine_tune_result_path', type=Path, required=True)
    parser.add_argument('--trial_number', type=int, required=True)
    parser.add_argument('--gpu_indexes', type=parse_gpu_indexes, required=True)
    parser.add_argument('--use_accelerate', action='store_true', default=False)

    return parser.parse_args(namespace=Args())


def main():
    args = parse_args()

    try:
        # accelerate
        if args.use_accelerate:
            local_rank = config('LOCAL_RANK', cast=int)
            rank = config('RANK', cast=int)
            world_size = config('WORLD_SIZE', cast=int)

            torch.cuda.set_device(local_rank)
            torch.distributed.init_process_group(
                backend='nccl',
                init_method='env://',
                world_size=world_size,
                rank=rank,
                device_id=torch.device('cuda', local_rank),
            )

        handler = DistributedDataParallelKwargs(find_unused_parameters=False)
        accelerator = Accelerator(kwargs_handlers=[handler]) if args.use_accelerate else None

        if accelerator:
            torch.cuda.set_device(accelerator.local_process_index)

        # login
        if accelerator and accelerator.is_main_process:
            wandb.login(key=WANDB_API_KEY)

        # read settings
        fine_tune_settings = JSONReaderUtil.read(
            args.fine_tune_settings_path, model=FineTuneSettings
        )

        # validate
        model_name = fine_tune_settings.model_settings.model_name
        metric_name = fine_tune_settings.optuna_settings.metric_name

        if model_name not in MODEL_NAMES:
            raise ValueError(f'Model {model_name} is not available')

        if metric_name not in METRIC_NAMES:
            raise ValueError(f'Metric {metric_name} is not available')

        # import model specification
        model_spec = import_model_spec(model_name)

        # select metric
        metric = Metric(metric_name)

        # optuna
        study_settings = fine_tune_settings.optuna_settings.study_settings
        study = load_study(
            study_name=f'{study_settings.study_name}-fine-tune-job-{args.fine_tune_job_id}',
            storage=study_settings.storage,
        )
        frozen_trial = next(trial for trial in study.trials if trial.number == args.trial_number)

        # fine tune
        model, tokenizer, prompt_collection, validate_dataset, test_dataset, train_duration = train(
            accelerator=accelerator,
            fine_tune_job_id=args.fine_tune_job_id,
            fine_tune_settings=fine_tune_settings,
            gpu_indexes=args.gpu_indexes,
            model_spec=model_spec,
            trial=frozen_trial,
        )

        # evaluate
        score, validate_duration, sequence_generator_adapter = validate(
            accelerator=accelerator,
            fine_tune_settings=fine_tune_settings,
            metric=metric,
            model=model,
            model_spec=model_spec,
            tokenizer=tokenizer,
            prompt_collection=prompt_collection,
            validate_dataset=validate_dataset,
        )

        # test
        test_result = test(
            accelerator=accelerator,
            fine_tune_settings=fine_tune_settings,
            sequence_generator_adapter=sequence_generator_adapter,
            model_spec=model_spec,
            tokenizer=tokenizer,
            prompt_collection=prompt_collection,
            test_dataset=test_dataset,
        )

        # create or update result
        if accelerator is None or accelerator.is_main_process:
            result = (
                Result(trial_results=[], test_results=[])
                if frozen_trial.number == 0
                else JSONReaderUtil.read(args.fine_tune_result_path, model=Result)
            )
            trial_result = TrialResult(
                number=frozen_trial.number,
                metric=metric.value,
                score=score,
                train_duration=train_duration,
                validate_duration=validate_duration,
            )
            result.trial_results.append(trial_result)
            result.test_results.append(test_result)

            JSONWriterUtil.write(args.fine_tune_result_path, model=result)

    finally:
        if torch.distributed.is_initialized():
            torch.distributed.barrier()
            torch.distributed.destroy_process_group()


if __name__ == '__main__':
    main()
