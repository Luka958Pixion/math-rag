from logging import INFO, basicConfig, getLogger
from pathlib import Path
from typing import cast

import huggingface_hub
import wandb

from datasets import load_dataset
from datasets.download import DownloadConfig
from decouple import config
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    PreTrainedModel,
    PreTrainedTokenizerBase,
    TrainerCallback,
    TrainerControl,
    TrainerState,
    TrainingArguments,
)
from transformers.configuration_utils import PretrainedConfig
from trl import SFTConfig, SFTTrainer

from .llama import init_llama_language_model, init_llama_tokenizer


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
        # TODO
        return control


def format_prompt(tokenizer: PreTrainedTokenizerBase, example: dict[str, str]):
    # https://huggingface.co/docs/transformers/main/en/internal/tokenization_utils#transformers.PreTrainedTokenizerBase.apply_chat_template
    prompt = tokenizer.apply_chat_template(
        conversation=...,
        tools=...,
        documents=...,
        chat_template=...,
        add_generation_prompt=...,
        continue_final_message=...,
        tokenize=...,
        padding=...,
        truncation=...,
        max_length=...,
        return_tensors=...,
        return_dict=...,
        return_assistant_tokens_mask=...,
        tokenizer_kwargs=...,
    )
    example.pop('prompt', None)

    return {'text': prompt}


def run():
    pretrained_config = PretrainedConfig(
        name_or_path=...,
        output_hidden_states=...,
        output_attentions=...,
        return_dict=...,
        is_encoder_decoder=...,
        is_decoder=...,
        cross_attention_hidden_size=...,
        add_cross_attention=...,
        tie_encoder_decoder=...,
        prune_heads=...,
        chunk_size_feed_forward=...,
        # Parameters for sequence generation
        max_length=...,
        min_length=...,
        do_sample=...,
        early_stopping=...,
        num_beams=...,
        num_beam_groups=...,
        diversity_penalty=...,
        temperature=...,
        top_k=...,
        top_p=...,
        typical_p=...,
        repetition_penalty=...,
        length_penalty=...,
        no_repeat_ngram_size=...,
        encoder_no_repeat_ngram_size=...,
        bad_words_ids=...,
        num_return_sequences=...,
        output_scores=...,
        return_dict_in_generate=...,
        forced_bos_token_id=...,
        forced_eos_token_id=...,
        remove_invalid_values=...,
        # Parameters for fine-tuning tasks
        architectures=...,
        finetuning_task=...,
        id2label=...,
        label2id=...,
        num_labels=...,
        task_specific_params=...,
        problem_type=...,
        # Parameters linked to the tokenizer
        tokenizer_class=...,
        prefix=...,
        bos_token_id=...,
        pad_token_id=...,
        eos_token_id=...,
        decoder_start_token_id=...,
        sep_token_id=...,
        # PyTorch specific parameters
        torchscript=...,
        tie_word_embeddings=...,
        torch_dtype=...,
        # TensorFlow specific parameters
        use_bfloat16=...,
        tf_legacy_loss=...,
    )
    # https://huggingface.co/docs/transformers/en/model_doc/auto#transformers.AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=...,
        inputs=...,
        config=...,
        cache_dir=...,
        force_download=...,
        resume_download=...,
        proxies=...,
        revision=...,
        subfolder=...,
        use_fast=...,
        tokenizer_type=...,
        trust_remote_code=...,
    )
    tokenizer = cast(PreTrainedTokenizerBase, tokenizer)
    init_llama_tokenizer(tokenizer)

    download_config = DownloadConfig(
        cache_dir=...,
        force_download=...,
        resume_download=...,
        local_files_only=...,
        proxies=...,
        user_agent=...,
        extract_compressed_file=...,
        force_extract=...,
        delete_extracted=...,
        extract_on_the_fly=...,
        use_etag=...,
        num_proc=...,
        max_retries=...,
        token=...,
        storage_options=...,
        download_desc=...,
        disable_tqdm=...,
    )

    # TODO hardcode everything except name/path
    # https://huggingface.co/docs/datasets/v3.5.1/en/package_reference/loading_methods#datasets.load_dataset
    dataset = load_dataset(
        path=...,
        name=...,
        data_dir=...,
        data_files=...,
        split=...,
        cache_dir=...,
        features=...,
        download_config=...,
        download_mode=...,
        verification_mode=...,
        keep_in_memory=...,
        save_infos=...,
        revision=...,
        token=...,
        streaming=...,
        num_proc=...,
        storage_options=...,
        trust_remote_code=...,
    )
    dataset = dataset.shuffle(seed=42)
    dataset = dataset.select(range(3000))
    dataset = dataset.map(format_prompt)

    # https://huggingface.co/docs/transformers/v4.51.3/en/main_classes/quantization#transformers.BitsAndBytesConfig
    bits_and_bytes_config = BitsAndBytesConfig(
        load_in_8bit=...,
        load_in_4bit=...,
        llm_int8_threshold=...,
        llm_int8_skip_modules=...,
        llm_int8_enable_fp32_cpu_offload=...,
        llm_int8_has_fp16_weight=...,
        bnb_4bit_compute_dtype=...,
        bnb_4bit_quant_type=...,
        bnb_4bit_use_double_quant=...,
        bnb_4bit_quant_storage=...,
    )

    # https://huggingface.co/docs/transformers/en/model_doc/auto#transformers.AutoModelForCausalLM.from_pretrained
    model = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=...,
        model_args=...,
        config=...,
        state_dict=...,
        cache_dir=...,
        from_tf=...,
        force_download=...,
        resume_download=...,
        proxies=...,
        output_loading_info=...,
        local_files_only=...,
        revision=...,
        trust_remote_code=...,
        code_revision=...,
    )
    model = cast(PreTrainedModel, model)
    init_llama_language_model(model)

    peft_config = LoraConfig(
        # https://huggingface.co/docs/peft/v0.15.0/en/package_reference/config#peft.config.PeftConfigMixin
        base_model_name_or_path=...,
        revision=...,
        peft_type=...,
        task_type=...,
        inference_mode=...,
        # https://huggingface.co/docs/peft/v0.15.0/en/package_reference/lora#peft.LoraConfig
        r=...,
        target_modules=...,
        exclude_modules=...,
        lora_alpha=...,
        lora_dropout=...,
        fan_in_fan_out=...,
        bias=...,
        use_rslora=...,
        modules_to_save=...,
        init_lora_weights=...,
        layers_to_transform=...,
        layers_pattern=...,
        rank_pattern=...,
        alpha_pattern=...,
        megatron_config=...,
        megatron_core=...,
        trainable_token_indices=...,
        loftq_config=...,
        eva_config=...,
        corda_config=...,
        use_dora=...,
        layer_replication=...,
        runtime_config=...,
        lora_bias=...,
    )

    # https://huggingface.co/docs/peft/v0.15.0/en/package_reference/peft_model#peft.prepare_model_for_kbit_training
    model = prepare_model_for_kbit_training(
        model=...,
        use_gradient_checkpointing=...,
        gradient_checkpointing_kwargs=...,
    )

    # https://huggingface.co/docs/peft/v0.15.0/en/package_reference/peft_model#peft.get_peft_model
    model = get_peft_model(
        model=...,
        peft_config=...,
        adapter_name=...,
        mixed=...,
        autocast_adapter_dtype=...,
        revision=...,
        low_cpu_mem_usage=...,
    )

    sft_config = SFTConfig(
        # https://huggingface.co/docs/transformers/v4.51.3/en/main_classes/trainer#transformers.TrainingArguments
        output_dir=...,
        overwrite_output_dir=...,
        do_train=...,
        do_eval=...,
        do_predict=...,
        eval_strategy=...,
        prediction_loss_only=...,
        per_device_train_batch_size=...,
        per_device_eval_batch_size=...,
        gradient_accumulation_steps=...,
        eval_accumulation_steps=...,
        eval_delay=...,
        torch_empty_cache_steps=...,
        weight_decay=...,
        adam_beta1=...,
        adam_beta2=...,
        adam_epsilon=...,
        max_grad_norm=...,
        num_train_epochs=...,
        max_steps=...,
        lr_scheduler_type=...,
        lr_scheduler_kwargs=...,
        warmup_ratio=...,
        warmup_steps=...,
        log_level=...,
        log_level_replica=...,
        log_on_each_node=...,
        logging_dir=...,
        logging_strategy=...,
        logging_first_step=...,
        logging_steps=...,
        logging_nan_inf_filter=...,
        save_strategy=...,
        save_steps=...,
        save_total_limit=...,
        save_safetensors=...,
        save_on_each_node=...,
        save_only_model=...,
        restore_callback_states_from_checkpoint=...,
        use_cpu=...,
        seed=...,
        data_seed=...,
        jit_mode_eval=...,
        use_ipex=...,
        bf16=...,
        fp16=...,
        fp16_opt_level=...,
        fp16_backend=...,
        half_precision_backend=...,
        bf16_full_eval=...,
        fp16_full_eval=...,
        tf32=...,
        local_rank=...,
        ddp_backend=...,
        tpu_num_cores=...,
        dataloader_drop_last=...,
        eval_steps=...,
        dataloader_num_workers=...,
        past_index=...,
        run_name=...,
        disable_tqdm=...,
        remove_unused_columns=...,
        label_names=...,
        load_best_model_at_end=...,
        metric_for_best_model=...,
        greater_is_better=...,
        ignore_data_skip=...,
        fsdp=...,
        fsdp_config=...,
        tp_size=...,
        deepspeed=...,
        accelerator_config=...,
        label_smoothing_factor=...,
        debug=...,
        optim=...,
        optim_args=...,
        group_by_length=...,
        length_column_name=...,
        report_to=...,
        ddp_find_unused_parameters=...,
        ddp_bucket_cap_mb=...,
        ddp_broadcast_buffers=...,
        dataloader_pin_memory=...,
        dataloader_persistent_workers=...,
        dataloader_prefetch_factor=...,
        skip_memory_metrics=...,
        push_to_hub=...,
        resume_from_checkpoint=...,
        hub_model_id=...,
        hub_strategy=...,
        hub_token=...,
        hub_private_repo=...,
        hub_always_push=...,
        gradient_checkpointing=...,
        gradient_checkpointing_kwargs=...,
        include_inputs_for_metrics=...,
        include_for_metrics=...,
        eval_do_concat_batches=...,
        auto_find_batch_size=...,
        full_determinism=...,
        torchdynamo=...,
        ray_scope=...,
        ddp_timeout=...,
        use_mps_device=...,
        torch_compile=...,
        torch_compile_backend=...,
        torch_compile_mode=...,
        include_tokens_per_second=...,
        include_num_input_tokens_seen=...,
        neftune_noise_alpha=...,
        optim_target_modules=...,
        batch_eval_metrics=...,
        eval_on_start=...,
        eval_use_gather_object=...,
        use_liger_kernel=...,
        average_tokens_across_devices=...,
        # https://huggingface.co/docs/trl/v0.17.0/en/sft_trainer#trl.SFTConfig
        model_init_kwargs=...,
        dataset_text_field=...,
        dataset_kwargs=...,
        dataset_num_proc=...,
        pad_token=...,
        max_length=...,
        packing=...,
        padding_free=...,
        eval_packing=...,
        learning_rate=...,
    )
    trainer = SFTTrainer(
        model=...,
        args=...,
        data_collator=...,
        train_dataset=...,
        eval_dataset=...,
        processing_class=...,
        callbacks=...,
        optimizers=...,
        optimizer_cls_and_kwargs=...,
        preprocess_logits_for_metrics=...,
        peft_config=...,
        formatting_func=...,
    )

    trainer.train(
        resume_from_checkpoint=...,
        trial=...,  # TODO pass optuna trial here
        ignore_keys_for_eval=...,
    )
    # NOTE dont use resume_from_checkpoint=True for the first run

    evaluation_results = trainer.evaluate(
        eval_dataset=..., ignore_keys=..., metric_key_prefix=...
    )
    trainer.model.save_pretrained(
        save_directory=...,
        is_main_process=...,
        state_dict=...,
        save_function=...,
        push_to_hub=...,
        max_shard_size=...,
        safe_serialization=...,
        variant=...,
        token=...,
        save_peft_format=...,
    )


def main():
    # TODO pass trial from optuna here
    # TODO which models are passed from optuna?

    # initialization
    huggingface_hub.login(token=HF_TOKEN)
    wandb.login(key=WANDB_API_KEY)
    wandb.init(project=WANDB_PROJECT, name='TinyLlama-1.1B-qlora')

    run()


if __name__ == '__main__':
    main()
