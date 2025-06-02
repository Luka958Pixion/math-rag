import json

from logging import INFO, basicConfig, getLogger
from pathlib import Path
from typing import cast

import huggingface_hub
import wandb

from datasets import DatasetDict, load_dataset
from datasets.download import DownloadConfig
from decouple import config
from fine_tune_settings import FineTuneSettings
from metrics import compute_metrics
from optuna import Trial
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
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
from trl import SFTConfig, SFTTrainer

from .llama_3_1_8b import (
    format_prompt,
    formatting_func,
    init_language_model,
    init_tokenizer,
)


# huggingface
HF_HOME = Path(...)  # TODO and bind!
HF_USERNAME = config('HF_USERNAME', default=None)
HF_TOKEN = config('HF_TOKEN', default=None)

# weights and biases
WANDB_PROJECT = config('WANDB_PROJECT', default=None)
WANDB_API_KEY = config('WANDB_API_KEY', default=None)

# paths
TRAINER_STATE_PATH = HF_HOME / 'trainer' / 'state'
TRAINER_MODEL_PATH = HF_HOME / 'trainer' / 'model'


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


def main(trial: Trial, settings: FineTuneSettings):
    # login
    huggingface_hub.login(token=HF_TOKEN)
    wandb.login(key=WANDB_API_KEY)
    wandb.init(
        project=WANDB_PROJECT,
        name=f'{settings.model_settings.model_name}_{trial.study._study_id}_{trial._trial_id}_qlora',
    )

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

    dataset_dict = dataset_dict.map(
        lambda x: format_prompt(x, prompt), remove_columns=dataset_dict['train'].column_names
    )

    train_dataset = dataset_dict['train']
    validate_dataset = dataset_dict['validate']
    test_dataset = dataset_dict['test']

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
        output_dir=f'{TRAINER_STATE_PATH}/{trial._trial_id}',
        do_train=True,
        do_eval=True,
        do_predict=False,
        eval_strategy='steps',
        eval_steps=100,
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
        report_to='wandb',
        logging_strategy='steps',
        logging_steps=100,
        logging_first_step=True,
    )

    graceful_stop_callback = GracefulStopCallback()
    wandb_callback = WandbCallback(
        wandb_kwargs={
            'name': f'lora-optuna-run-{trial.number}',
            'tags': [
                f'r={r}',
                f'alpha={lora_alpha}',
                f'dropout={lora_dropout}',
            ],
            'notes': f'Optuna trial #{trial.number} with params {trial.params}',
        }
    )

    data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        data_collator=data_collator,
        train_dataset=train_dataset,
        eval_dataset=validate_dataset,
        test_dataset=test_dataset,
        processing_class=tokenizer,
        callbacks=[graceful_stop_callback, wandb_callback],
        optimizer_cls_and_kwargs=(AdamW, settings.optimizer_settings.model_dump()),
        preprocess_logits_for_metrics=False,
        compute_metrics=compute_metrics,
        formatting_func=lambda batch: formatting_func(tokenizer, batch),
    )
    trainer.train(
        resume_from_checkpoint=True,
        trial=trial,
        ignore_keys_for_eval=['past_key_values', 'hidden_states', 'attentions'],
    )
    trainer.model.save_pretrained(
        save_directory=f'{TRAINER_MODEL_PATH}/{trial._trial_id}',
        push_to_hub=False,
        token=None,
        save_peft_format=True,
    )

    # evaluate
    eval_results = trainer.evaluate(eval_dataset=validate_dataset)
    f1 = eval_results['eval_f1']

    return f1


if __name__ == '__main__':
    main()
