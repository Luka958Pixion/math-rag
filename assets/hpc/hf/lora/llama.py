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
        # TODO new PeftConfig
        # base_model_name_or_path=...,
        # revision=...,
        # peft_type=...,
        # task_type=...,
        # inference_mode=...,
        # TODO new Lora
        # r=...,
        # target_modules=...,
        # exclude_modules=...,
        # lora_alpha=...,
        # lora_dropout=...,
        # fan_in_fan_out=...,
        # bias=...,
        # use_rslora=...,
        # modules_to_save=...,
        # init_lora_weights=...,
        # layers_to_transform=...,
        # layers_pattern=...,
        # rank_pattern=...,
        # alpha_pattern=...,
        # megatron_config=...,
        # megatron_core=...,
        # trainable_token_indices=...,
        # loftq_config=...,
        # eva_config=...,
        # corda_config=...,
        # use_dora=...,
        # layer_replication=...,
        # runtime_config=...,
        # lora_bias=...,
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
        # TODO new TrainingArguments
        # output_dir=...,
        # overwrite_output_dir=...,
        # do_train=...,
        # do_eval=...,
        # do_predict=...,
        # eval_strategy=...,
        # prediction_loss_only=...,
        # per_device_train_batch_size=...,
        # per_device_eval_batch_size=...,
        # gradient_accumulation_steps=...,
        # eval_accumulation_steps=...,
        # eval_delay=...,
        # torch_empty_cache_steps=...,
        # learning_rate=...,
        # weight_decay=...,
        # adam_beta1=...,
        # adam_beta2=...,
        # adam_epsilon=...,
        # max_grad_norm=...,
        # num_train_epochs=...,
        # max_steps=...,
        # lr_scheduler_type=...,
        # lr_scheduler_kwargs=...,
        # warmup_ratio=...,
        # warmup_steps=...,
        # log_level=...,
        # log_level_replica=...,
        # log_on_each_node=...,
        # logging_dir=...,
        # logging_strategy=...,
        # logging_first_step=...,
        # logging_steps=...,
        # logging_nan_inf_filter=...,
        # save_strategy=...,
        # save_steps=...,
        # save_total_limit=...,
        # save_safetensors=...,
        # save_on_each_node=...,
        # save_only_model=...,
        # restore_callback_states_from_checkpoint=...,
        # use_cpu=...,
        # seed=...,
        # data_seed=...,
        # jit_mode_eval=...,
        # use_ipex=...,
        # bf16=...,
        # fp16=...,
        # fp16_opt_level=...,
        # fp16_backend=...,
        # half_precision_backend=...,
        # bf16_full_eval=...,
        # fp16_full_eval=...,
        # tf32=...,
        # local_rank=...,
        # ddp_backend=...,
        # tpu_num_cores=...,
        # dataloader_drop_last=...,
        # eval_steps=...,
        # dataloader_num_workers=...,
        # past_index=...,
        # run_name=...,
        # disable_tqdm=...,
        # remove_unused_columns=...,
        # label_names=...,
        # load_best_model_at_end=...,
        # metric_for_best_model=...,
        # greater_is_better=...,
        # ignore_data_skip=...,
        # fsdp=...,
        # fsdp_config=...,
        # tp_size=...,
        # deepspeed =...,
        # accelerator_config=...,
        # label_smoothing_factor=...,
        # debug=...,
        # optim=...,
        # optim_args=...,
        # group_by_length=...,
        # length_column_name=...,
        # report_to=...,
        # ddp_find_unused_parameters=...,
        # ddp_bucket_cap_mb=...,
        # ddp_broadcast_buffers=...,
        # dataloader_pin_memory=...,
        # dataloader_persistent_workers=...,
        # dataloader_prefetch_factor=...,
        # skip_memory_metrics=...,
        # push_to_hub=...,
        # resume_from_checkpoint=...,
        # hub_model_id=...,
        # hub_strategy=...,
        # hub_token=...,
        # hub_private_repo=...,
        # hub_always_push=...,
        # gradient_checkpointing=...,
        # gradient_checkpointing_kwargs=...,
        # include_inputs_for_metrics=...,
        # include_for_metrics=...,
        # eval_do_concat_batches=...,
        # auto_find_batch_size=...,
        # full_determinism=...,
        # torchdynamo=...,
        # ray_scope=...,
        # ddp_timeout=...,
        # use_mps_device=...,
        # torch_compile=...,
        # torch_compile_backend=...,
        # torch_compile_mode=...,
        # include_tokens_per_second=...,
        # include_num_input_tokens_seen=...,
        # neftune_noise_alpha=...,
        # optim_target_modules=...,
        # batch_eval_metrics=...,
        # eval_on_start=...,
        # eval_use_gather_object=...,
        # use_liger_kernel=...,
        # average_tokens_across_devices=...,
        # TODO new SFTConfig
        # model_init_kwargs=...,
        # dataset_text_field=...,
        # dataset_kwargs=...,
        # dataset_num_proc=...,
        # pad_token=...,
        # max_length=...,
        # packing=...,
        # padding_free=...,
        # eval_packing=...,
        # learning_rate=...,
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
        # TODO new SFTTrainer
        # model=...,
        # args=...,
        # data_collator=...,
        # train_dataset=...,
        # eval_dataset=...,
        # processing_class=...,
        # callbacks=...,
        # optimizers=...,
        # optimizer_cls_and_kwargs=...,
        # preprocess_logits_for_metrics=...,
        # peft_config=...,
        # formatting_func=...,
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
