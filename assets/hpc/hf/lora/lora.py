import os
import subprocess

from datetime import timedelta
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from threading import Event, Thread
from time import sleep

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


# current job
PBS_JOB_ID = os.environ['PBS_JOBID']

# squid proxy
HTTP_PROXY = 'http://10.150.1.1:3128'
HTTPS_PROXY = 'http://10.150.1.1:3128'

# weights and biases
WANDB_PROJECT = config('WANDB_PROJECT', default=None)
WANDB_API_KEY = config('WANDB_API_KEY', default=None)

# paths
ENV_PATH = Path('.env.hpc.hf.lora')

# thresholds
WALLTIME_THRESHOLD = timedelta(minutes=30)


basicConfig(
    level=INFO, format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s'
)
logger = getLogger(__name__)


class GracefulStopCallback(TrainerCallback):
    def __init__(self, training_stop_event: Event):
        self._training_stop_event = training_stop_event

    def on_step_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ):
        # triggered at the end of every training step
        if self._training_stop_event.is_set():
            logger.warning('Graceful stop event detected, stopping training...')
            control.should_training_stop = True

        return control


class FineTuningProcessorThread(Thread):
    def __init__(self, training_stop_event: Event, training_done_event: Event):
        super().__init__(name=self.__class__.__name__)

        self._training_stop_event = training_stop_event
        self._training_done_event = training_done_event

    def run(self):
        logger.info(f'{self.__class__.__name__} started')

        tokenizer_name = 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'
        tokenizer: LlamaTokenizerFast = AutoTokenizer.from_pretrained(tokenizer_name)
        logger.info(f'tokenizer: {type(tokenizer)}')

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
        logger.info(f'model: {type(tokenizer)}')

        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=False)
        tokenizer.pad_token = '<PAD>'
        tokenizer.padding_side = 'left'
        logger.info(f'tokenizer2: {type(tokenizer)}')

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

        self._training_done_event.set()
        logger.info(f'{self.__class__.__name__} exited')


class WalltimeTrackerThread(Thread):
    def __init__(self, training_stop_event: Event, training_done_event: Event):
        super().__init__(name=self.__class__.__name__)

        self._training_stop_event = training_stop_event
        self._training_done_event = training_done_event

    def run(self):
        logger.info(f'{self.__class__.__name__} started')

        DELAY = 3 * 60
        cmd = (
            f'qstat -f {PBS_JOB_ID} | '
            "awk -F'= ' "
            "'/Resource_List.walltime/ { walltime = $2 } "
            '/resources_used.walltime/ { used = $2 } '
            'END { print walltime "\\n" used }\''
        )

        while True:
            if self._training_done_event.is_set():
                break

            # read walltime
            result = subprocess.run(
                cmd, check=True, capture_output=True, text=True, shell=True
            )
            walltimes = result.stdout.strip().splitlines()

            if len(walltimes) == 1:
                sleep(DELAY)
                continue

            hours, minutes, seconds = map(int, walltimes[0].split(':'))
            walltime = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            hours, minutes, seconds = map(int, walltimes[1].split(':'))
            walltime_used = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            walltime_left = walltime - walltime_used

            if walltime_left < WALLTIME_THRESHOLD:
                self._training_stop_event.set()
                break

            sleep(DELAY)

        logger.info(f'{self.__class__.__name__} exited')


def main():
    # initialization
    training_stop_event = Event()
    training_done_event = Event()

    # threads
    fine_tuning_processor_thread = FineTuningProcessorThread(
        training_stop_event, training_done_event
    )
    walltime_tracker_thread = WalltimeTrackerThread(
        training_stop_event, training_done_event
    )

    fine_tuning_processor_thread.start()
    walltime_tracker_thread.start()

    fine_tuning_processor_thread.join()
    walltime_tracker_thread.join()


if __name__ == '__main__':
    main()
