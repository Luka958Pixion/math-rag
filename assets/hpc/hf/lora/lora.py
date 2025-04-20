from logging import INFO, basicConfig, getLogger
from pathlib import Path
from threading import Thread

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


WANDB_PROJECT = config('WANDB_PROJECT', default=None)
WANDB_ENTITY = config('WANDB_ENTITY', default=None)
WANDB_NAME = config('WANDB_NAME', default=None)

CLIENT_SIF_PATH = Path('client.sif')
ENV_PATH = Path('.env.hpc.hf.lora')


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
        # TODO use something instead of env var
        # if os.path.exists("STOP_TRAINING"):
        #    control.should_training_stop = True

        return control


class FineTuningProcessorThread(Thread):
    def __init__(self):
        super().__init__(name=self.__class__.__name__)

    def run(self):
        tokenizer_name = 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'
        tokenizer: LlamaTokenizerFast = AutoTokenizer.from_pretrained(tokenizer_name)

        def format_prompt(example):
            chat = example['messages']
            prompt = tokenizer.apply_chat_template(chat, tokenize=False)

            return {'text': prompt}

        dataset_path = 'HuggingFaceH4/ultrachat_200k'
        dataset = (
            load_dataset(dataset_path, split='test_sft')
            .shuffle(seed=42)
            .select(range(3000))
        )
        dataset = dataset.map(format_prompt)

        model_name = 'TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T'

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type='nf4',
            bnb_4bit_compute_dtype='float16',
            bnb_4bit_use_double_quant=True,
        )

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map='auto',
            quantization_config=bnb_config,
        )
        model.config.use_cache = False
        model.config.pretraining_tp = 1

        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=False)
        tokenizer.pad_token = '<PAD>'
        tokenizer.padding_side = 'left'

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
            output_dir='TinyLlama-1.1B-qlora',
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
            logging_dir='./logs',
            logging_steps=10,
        )
        trainer = SFTTrainer(
            model=model,
            train_dataset=dataset,
            tokenizer=tokenizer,
            args=sft_config,
            peft_config=peft_config,
        )

        trainer.add_callback(GracefulStopCallback())
        trainer.train(resume_from_checkpoint=True)
        trainer.model.save_pretrained('TinyLlama-1.1B-qlora')


class WalltimeTrackerThread(Thread):
    def __init__(self):
        super().__init__(name=self.__class__.__name__)

    def run(self):
        pass


def main():
    fine_tuning_processor_thread = FineTuningProcessorThread()
    walltime_tracker_thread = WalltimeTrackerThread()

    fine_tuning_processor_thread.start()
    walltime_tracker_thread.start()

    fine_tuning_processor_thread.join()
    walltime_tracker_thread.join()


if __name__ == '__main__':
    main()
