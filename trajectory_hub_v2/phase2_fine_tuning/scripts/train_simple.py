#!/usr/bin/env python3
"""
Script simplificado de entrenamiento XYNZ
Evita problemas de tokenización y es fácil de ejecutar
"""
import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
from datetime import datetime
import json

print("=== Entrenamiento XYNZ - DeepSeek Fine-tuning ===")
print(f"Inicio: {datetime.now()}")

# Verificar GPU
if torch.cuda.is_available():
    print(f"GPU detectada: {torch.cuda.get_device_name(0)}")
    print(f"Memoria GPU: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
else:
    print("⚠️  No se detectó GPU, usando CPU (será muy lento)")

# Configuración 4-bit
print("\n📊 Configurando cuantización 4-bit...")
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

# Cargar modelo y tokenizador
print("\n🔄 Cargando modelo DeepSeek-R1-Distill-Qwen-7B...")
model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

# Preparar modelo para entrenamiento
model = prepare_model_for_kbit_training(model)

# Configuración LoRA
print("\n⚙️  Configurando LoRA...")
lora_config = LoraConfig(
    r=32,
    lora_alpha=64,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
print(f"Parámetros entrenables: {model.print_trainable_parameters()}")

# Cargar dataset
print("\n📚 Cargando dataset XYNZ...")
data_path = "/workspace/xynz-finetuning/trajectory_hub_v2/phase2_fine_tuning/dataset/processed/alpaca"

# Función simple para cargar JSONL
def load_jsonl(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line.strip()))
    return data

# Cargar datos
train_data = load_jsonl(f"{data_path}/train.jsonl")
val_data = load_jsonl(f"{data_path}/validation.jsonl")

print(f"Ejemplos de entrenamiento: {len(train_data)}")
print(f"Ejemplos de validación: {len(val_data)}")

# Convertir a formato de texto simple
def format_example(example):
    instruction = example.get('instruction', '')
    output = example.get('output', '')
    # Formato simple sin tokens especiales complejos
    return f"Instrucción: {instruction}\nRespuesta: {output}"

# Preparar datasets
train_texts = [format_example(ex) for ex in train_data]
val_texts = [format_example(ex) for ex in val_data]

# Guardar como archivos de texto temporales
with open('/tmp/train.txt', 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(train_texts))

with open('/tmp/val.txt', 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(val_texts))

# Cargar con datasets
train_dataset = load_dataset('text', data_files='/tmp/train.txt')['train']
eval_dataset = load_dataset('text', data_files='/tmp/val.txt')['train']

# Función de tokenización simple
def tokenize_function(examples):
    return tokenizer(
        examples['text'],
        truncation=True,
        padding='max_length',
        max_length=512
    )

# Tokenizar datasets
print("\n🔄 Tokenizando datasets...")
tokenized_train = train_dataset.map(tokenize_function, batched=True, remove_columns=['text'])
tokenized_eval = eval_dataset.map(tokenize_function, batched=True, remove_columns=['text'])

# Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

# Configurar argumentos de entrenamiento
print("\n🎯 Configurando entrenamiento...")
training_args = TrainingArguments(
    output_dir="/workspace/xynz-finetuning/trajectory_hub_v2/phase2_fine_tuning/models/deepseek-xynz-lora",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=8,
    gradient_checkpointing=True,
    warmup_steps=100,
    logging_steps=10,
    save_steps=500,
    eval_steps=500,
    evaluation_strategy="steps",
    save_strategy="steps",
    load_best_model_at_end=True,
    learning_rate=1e-4,
    fp16=True,
    optim="paged_adamw_8bit",
    report_to=["tensorboard"],
    push_to_hub=False,
)

# Crear trainer
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_eval,
)

# Entrenar
print("\n🚀 Iniciando entrenamiento...")
print(f"Épocas: {training_args.num_train_epochs}")
print(f"Batch size efectivo: {training_args.per_device_train_batch_size * training_args.gradient_accumulation_steps}")
print(f"Pasos totales estimados: {len(tokenized_train) // (training_args.per_device_train_batch_size * training_args.gradient_accumulation_steps) * training_args.num_train_epochs}")

# Iniciar entrenamiento
trainer.train()

# Guardar modelo final
print("\n💾 Guardando modelo final...")
trainer.save_model()
tokenizer.save_pretrained(training_args.output_dir)

print(f"\n✅ Entrenamiento completado: {datetime.now()}")
print(f"Modelo guardado en: {training_args.output_dir}")