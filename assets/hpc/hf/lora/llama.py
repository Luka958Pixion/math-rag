from logging import INFO, basicConfig, getLogger
from pathlib import Path

import huggingface_hub
import wandb

from datasets import load_dataset
from decouple import config
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainerCallback,
    TrainerControl,
    TrainerState,
    TrainingArguments,
)
from transformers.models.llama.tokenization_llama_fast import LlamaTokenizerFast
from trl import SFTConfig, SFTTrainer


# huggingface
HF_TOKEN = config('HF_TOKEN', default=None)

# weights and biases
WANDB_PROJECT = config('WANDB_PROJECT', default=None)
WANDB_API_KEY = config('WANDB_API_KEY', default=None)

# models
MODEL_NAME = config('MODEL_NAME', default=None)
TOKENIZER_NAME = config('TOKENIZER_NAME', default=None)

# dataset
DATASET_PATH = config('DATASET_PATH', default=None)

# paths
CACHE_DIR_PATH = Path('data')


basicConfig(
    level=INFO, format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s'
)
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


def run():
    tokenizer: LlamaTokenizerFast = AutoTokenizer.from_pretrained(
        TOKENIZER_NAME, trust_remote_code=True, cache_dir=CACHE_DIR_PATH
    )
    logger.info(f'tokenizer: {type(tokenizer)}')

    def format_prompt(example: dict):
        prompt = tokenizer.apply_chat_template(example['messages'], tokenize=False)
        example.pop('prompt', None)

        return {'text': prompt}

    dataset = (
        load_dataset(DATASET_PATH, split='test_sft')
        .shuffle(seed=42)
        .select(range(3000))
    )
    dataset = dataset.map(format_prompt)

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type='nf4',
        bnb_4bit_compute_dtype='float16',
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        device_map='auto',
        quantization_config=bnb_config,
        cache_dir=CACHE_DIR_PATH,
    )
    model.config.use_cache = False
    model.config.pretraining_tp = 1

    tokenizer.pad_token = '<PAD>'
    tokenizer.padding_side = 'left'
    tokenizer.chat_template = "{% for message in messages %}{{ message['role'] }}: {{ message['content'] }}\n{% endfor %}"

    peft_config = LoraConfig(
        lora_alpha=32,
        lora_dropout=0.1,
        r=64,
        bias='none',
        task_type='CAUSAL_LM',
        target_modules=[
            'k_proj',
            'gate_proj',
            'v_proj',
            'up_proj',
            'q_proj',
            'o_proj',
            'down_proj',
        ],
    )

    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, peft_config)

    sft_config = SFTConfig(
        output_dir='output/TinyLlama-1.1B-qlora',
        dataset_text_field='text',
        max_seq_length=512,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        optim='paged_adamw_32bit',
        learning_rate=2e-4,
        lr_scheduler_type='cosine',
        num_train_epochs=1,
        fp16=True,
        gradient_checkpointing=True,
        report_to='wandb',
        logging_steps=10,
        label_names=['labels'],
        packing=True,
    )
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        eval_dataset=...,
        processing_class=tokenizer,
        args=sft_config,
        peft_config=peft_config,
        callbacks=[
            GracefulStopCallback(),
        ],
    )

    trainer.train()  # NOTE dont use resume_from_checkpoint=True for the first run
    evaluation_results = trainer.evaluate(...)
    trainer.model.save_pretrained(
        'TinyLlama-1.1B-qlora', push_to_hub=False, repo_id=None
    )


def main():
    # initialization
    huggingface_hub.login(token=HF_TOKEN)
    wandb.login(key=WANDB_API_KEY)
    wandb.init(project=WANDB_PROJECT, name='TinyLlama-1.1B-qlora')

    run()


if __name__ == '__main__':
    main()
