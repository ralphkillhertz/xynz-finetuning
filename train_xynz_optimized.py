#!/usr/bin/env python3
"""
Training script optimizado para XYNZ Fine-tuning
Modelo: DeepSeek-R1-Distill-Qwen-7B -> DeepSeek-XYNZ-4B
Optimizaciones: 3 épocas, LoRA mejorado, mejor learning rate
"""

import torch
import os
from datetime import datetime
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType
from datasets import load_dataset
import warnings
warnings.filterwarnings("ignore")

print("=" * 60)
print("🎯 XYNZ Fine-tuning - Configuración Optimizada")
print("=" * 60)
print(f"🕐 Inicio: {datetime.now()}")
print(f"🖥️  GPU: {torch.cuda.get_device_name(0)}")
print(f"💾 Memoria GPU: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
print(f"🔧 PyTorch: {torch.__version__}")
print("=" * 60)

# Configuración 4-bit optimizada
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True
)

# Cargar modelo
model_id = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
print(f"\n�� Cargando modelo base: {model_id}")
print("   Esto puede tardar 2-3 minutos...")

# Tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"  # Para evitar warnings

# Modelo con cuantización
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.float16,
)
print("✅ Modelo cargado exitosamente")

# Preparar modelo para k-bit training
model.config.use_cache = False  # Importante para gradient checkpointing
model = prepare_model_for_kbit_training(model)

# Configuración LoRA MEJORADA
print("\n🔧 Configurando LoRA optimizado...")
lora_config = LoraConfig(
    r=32,  # Aumentado de 16 a 32 para más capacidad
    lora_alpha=64,  # Alpha = 2*r es una buena práctica
    target_modules=[
        "q_proj", "v_proj", "k_proj", "o_proj",  # Attention
        "gate_proj", "up_proj", "down_proj"      # MLP layers - NUEVO
    ],
    lora_dropout=0.05,  # Reducido de 0.1 para mejor aprendizaje
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

# Aplicar LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# Habilitar gradient checkpointing para ahorrar memoria
model.enable_input_require_grads()
model.gradient_checkpointing_enable()

# Cargar dataset
print("\n📊 Cargando dataset XYNZ...")
dataset = load_dataset("json", data_files={
    "train": "dataset/processed/alpaca/train.jsonl",
    "validation": "dataset/processed/alpaca/validation.jsonl"
})
print(f"✅ Dataset cargado - Train: {len(dataset['train']):,} | Val: {len(dataset['validation']):,}")

# Función de tokenización mejorada
def tokenize_function(examples):
    """Tokeniza con formato optimizado para instrucciones"""
    texts = []
    for inst, out in zip(examples["instruction"], examples["output"]):
        # Formato mejorado con tokens especiales
        text = f"""<|im_start|>system
Eres un experto en audio espacializado y sistemas SPAT. Respondes de forma precisa y técnica.
<|im_end|>
<|im_start|>user
{inst}
<|im_end|>
<|im_start|>assistant
{out}
<|im_end|>"""
        texts.append(text)

    # Tokenizar con configuración optimizada
    model_inputs = tokenizer(
        texts,
        truncation=True,
        padding="max_length",
        max_length=384,  # Aumentado de 256 para instrucciones más complejas
        return_tensors="pt"
    )

    # Labels = input_ids para causal LM
    model_inputs["labels"] = model_inputs["input_ids"].copy()

    return model_inputs

# Tokenizar datasets
print("\n🔄 Tokenizando datasets...")
tokenized_dataset = dataset.map(
    tokenize_function,
    batched=True,
    num_proc=4,  # Paralelizar
    remove_columns=dataset["train"].column_names
)
print("✅ Tokenización completada")

# Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,  # No masked language modeling
)

# Configuración de entrenamiento OPTIMIZADA
print("\n⚙️ Configurando parámetros de entrenamiento optimizados...")
training_args = TrainingArguments(
    output_dir="./models/deepseek-xynz-lora-optimized",

    # Épocas y batch
    num_train_epochs=3,  # Aumentado de 1 a 3
    per_device_train_batch_size=8,  # Aumentado si la GPU aguanta
    per_device_eval_batch_size=8,
    gradient_accumulation_steps=2,  # Reducido porque aumentamos batch size

    # Learning rate optimizado
    learning_rate=5e-5,  # Reducido de 1e-4
    weight_decay=0.01,  # Añadido para regularización
    warmup_ratio=0.1,  # 10% de warmup es mejor que steps fijos
    lr_scheduler_type="cosine",  # Mejor que linear

    # Logging y saving
    logging_steps=25,  # Más frecuente
    save_strategy="epoch",  # Guardar cada época
    evaluation_strategy="steps",
    eval_steps=250,  # Evaluar 4 veces por época aprox
    save_total_limit=3,
    load_best_model_at_end=True,  # Cargar el mejor modelo al final
    metric_for_best_model="eval_loss",
    greater_is_better=False,

    # Optimizaciones
    fp16=True,
    optim="paged_adamw_8bit",  # Optimizador eficiente en memoria
    gradient_checkpointing=True,
    max_grad_norm=0.3,

    # Otros
    report_to="none",  # Cambiar a "wandb" si quieres logging
    run_name="xynz-spatial-audio-optimized",
    seed=42,

    # Para debugging
    logging_first_step=True,
    logging_nan_inf_filter=True,
)

# Crear trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"],
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# Callback para monitorear progreso
class ProgressCallback:
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs:
            print(f"\n📈 Step {state.global_step}: Loss={logs.get('loss', 0):.4f}")

trainer.add_callback(ProgressCallback())

# ENTRENAR
print("\n" + "=" * 60)
print("🚀 INICIANDO ENTRENAMIENTO OPTIMIZADO")
print(f"📊 Total de pasos: ~{len(tokenized_dataset['train']) // (training_args.per_device_train_batch_size * training_args.gradient_accumulation_steps) * training_args.num_train_epochs}")
print(f"⏱️  Tiempo estimado: 4-6 horas")
print("=" * 60 + "\n")

# Guardar estado inicial de memoria
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    print(f"💾 Memoria GPU antes de entrenar: {torch.cuda.memory_allocated()/1e9:.2f} GB")

# Entrenar
start_time = datetime.now()
train_result = trainer.train()
end_time = datetime.now()

# Estadísticas finales
print("\n" + "=" * 60)
print("✅ ENTRENAMIENTO COMPLETADO")
print(f"⏱️  Tiempo total: {end_time - start_time}")
print(f"📉 Loss final: {train_result.metrics['train_loss']:.4f}")
print("=" * 60)

# Guardar modelo final
print("\n💾 Guardando modelo fine-tuneado...")
trainer.save_model()
tokenizer.save_pretrained(training_args.output_dir)

# Guardar métricas
with open(os.path.join(training_args.output_dir, "training_metrics.txt"), "w") as f:
    f.write(f"Fecha: {datetime.now()}\n")
    f.write(f"Tiempo de entrenamiento: {end_time - start_time}\n")
    f.write(f"Métricas finales:\n")
    for key, value in train_result.metrics.items():
        f.write(f"  {key}: {value}\n")

print("\n🎉 ¡Proceso completado exitosamente!")
print(f"📂 Modelo guardado en: {training_args.output_dir}")
print("\n💡 Siguiente paso: Convertir a GGUF o mergear con modelo base para uso en producción")
