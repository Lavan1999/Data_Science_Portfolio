# Libraries and imports
import os
import json
import random
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import torch
from datasets import load_dataset, Dataset
from transformers import set_seed
from tokenizers import Tokenizer
import sentencepiece as spm

from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template
from trl import SFTTrainer, SFTConfig


# CONFIGURATION

DATA_DIR = "./dataset_out"
OUT_DIR  = "outputs_llama31_8b_hscode"
BASE     = "meta-llama/Llama-3.1-8B-Instruct"

SEED = 3407 #42
MAX_SEQ_LEN = 4096
PER_DEVICE_BS = 2
GRAD_ACCUM = 8
MAX_STEPS = 2
LR = 1.5e-4

DO_MERGE = True
QUANTS = ["f16", "q8_0"]
CUSTOM_MODEFILE = "custom_Modelfile.txt"
SCRIPT_DIR = Path(__file__).resolve().parent
LLAMACPP_DIR = SCRIPT_DIR / "llama.cpp"
#LLAMACPP_DIR = Path(__file__).resolve().parent / "llama.cpp"
VAL_SPLIT_RATIO = 0.05



# HELPERS AND UTILITIES

def read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

def write_jsonl_iterable(path: Path, iterable):
    with path.open("w", encoding="utf-8") as f:
        for obj in iterable:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def maybe_create_val_split(data_dir: Path, val_ratio: float = VAL_SPLIT_RATIO):
    """Create val.jsonl if missing."""
    train_path = data_dir / "train.jsonl"
    val_path = data_dir / "val.jsonl"

    if not train_path.exists():
        raise FileNotFoundError(f"Missing {train_path}")

    if val_path.exists():
        print(f"[INFO] Found existing validation file: {val_path}")
        return val_path

    print("[INFO] Creating validation split...")
    entries = list(read_jsonl(train_path))
    random.Random(SEED).shuffle(entries)

    n_val = max(1, int(len(entries) * val_ratio))
    val_entries = entries[:n_val]
    train_entries = entries[n_val:]

    write_jsonl_iterable(train_path, train_entries)
    write_jsonl_iterable(val_path, val_entries)

    print(f"[INFO] Created val.jsonl with {len(val_entries)} entries.")
    return val_path

def load_split(name: str, data_dir: Path) -> Optional[Dataset]:
    p = data_dir / f"{name}.jsonl"
    if not p.exists():
        return None
    return load_dataset("json", data_files=str(p), split="train")

def write_modelfile(custom_modelfile: Path, chosen_gguf: str, out_path: Path):
    if custom_modelfile.exists():
        try:
            lines = custom_modelfile.read_text(encoding="utf-8").splitlines()
        except:
            lines = []

        final = []
        for line in lines:
            if line.strip().startswith("FROM "):
                final.append(f"FROM {chosen_gguf}")
            else:
                final.append(line)

        if not final:
            final = [f"FROM {chosen_gguf}", 'TEMPLATE "{{ .Prompt }}"']

        out_path.write_text("\n".join(final), encoding="utf-8")
    else:
        out_path.write_text(f"FROM {chosen_gguf}\nTEMPLATE \"{{{{ .Prompt }}}}\"", encoding="utf-8")

    print(f"[INFO] Wrote Modelfile -> {out_path}")

def ensure_llama_cpp(llamacpp_dir: Path):
    if not llamacpp_dir.exists():
        print("[INFO] Cloning llama.cpp...")
        subprocess.run(["git", "clone", "https://github.com/ggerganov/llama.cpp.git", str(llamacpp_dir)], check=True)
    else:
        print("[INFO] Updating llama.cpp...")
        subprocess.run(["git", "-C", str(llamacpp_dir), "pull"], check=True)

    build_dir = llamacpp_dir / "build"
    llama_quantize = build_dir / "bin" / "llama-quantize"

    if llama_quantize.exists():
        print("[INFO] llama.cpp already built.")
        return

    build_dir.mkdir(parents=True, exist_ok=True)
    print("[INFO] Building llama.cpp...")
    subprocess.run(["cmake", ".."], cwd=build_dir, check=True)
    subprocess.run(["cmake", "--build", ".", "-j"], cwd=build_dir, check=True)
    print("[INFO] llama.cpp build complete.")

def rebuild_tokenizer_model_from_json(tokenizer_json_path: Path, output_path: Path):
    print("[INFO] Rebuilding tokenizer.model ...")
    tok = Tokenizer.from_file(str(tokenizer_json_path))
    vocab = tok.get_vocab()

    vocab_txt = output_path.with_suffix(".vocab.txt")
    with vocab_txt.open("w", encoding="utf-8") as f:
        for token, idx in sorted(vocab.items(), key=lambda kv: kv[1]):
            f.write(token.replace("\n", " ") + "\n")

    sp_model_prefix = str(output_path.with_suffix(""))
    vocab_size = min(max(8000, len(vocab)), len(vocab))

    spm.SentencePieceTrainer.Train(
        f"--input={vocab_txt} "
        f"--model_prefix={sp_model_prefix} "
        f"--vocab_size={vocab_size} "
        "--character_coverage=1.0 "
        " --model_type=bpe"
    )
    print(f"[INFO] Rebuilt tokenizer.model at: {output_path}")

def ensure_tokenizer_model(tokenizer, merged_dir: Path, base_model_id: str):
    tokenizer.save_pretrained(merged_dir)
    tok_path = merged_dir / "tokenizer.model"

    if not tok_path.exists() or tok_path.stat().st_size == 0:
        print("[WARN] tokenizer.model missing, rebuilding...")
        tok_json = merged_dir / "tokenizer.json"
        if tok_json.exists():
            rebuild_tokenizer_model_from_json(tok_json, tok_path)

    if not tok_path.exists():
        raise FileNotFoundError("tokenizer.model missing even after rebuild.")



# MAIN PIPELINE

def main():
    data_dir = Path(DATA_DIR)
    ensure_dir(data_dir)
    set_seed(SEED)
    random.seed(SEED)

    val_path = maybe_create_val_split(data_dir)

    # Load data
    train_ds = load_split("train", data_dir)
    val_ds = load_split("val", data_dir)

    if train_ds is None:
        raise FileNotFoundError("train.jsonl missing")

    assert "messages" in train_ds.column_names

    # Load model
    print(f"[INFO] Loading base model: {BASE}")

    # Auto–bf16 selection
    try:
        bf16_supported = getattr(torch.cuda, "is_bf16_supported", lambda: False)()
    except:
        bf16_supported = False

    dtype_choice = torch.bfloat16 if bf16_supported else torch.float16
    print(f"[INFO] Using dtype: {dtype_choice}")

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=BASE,
        max_seq_length=MAX_SEQ_LEN,
        dtype=dtype_choice,
        load_in_4bit=False,
        full_finetuning=False,
        device_map="auto",
    )
    model = FastLanguageModel.for_training(model)

    # Chat template
    tokenizer = get_chat_template(tokenizer, chat_template="llama-3.1")
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token

    # Convert to text
    def to_text(batch):
        return {"text": [
            tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)
            for msgs in batch["messages"]
        ]}

    print("[INFO] Applying chat template to dataset...")
    train_ds = train_ds.map(to_text, batched=True, remove_columns=train_ds.column_names)
    #val_ds = val_ds.map(to_text, batched=True, remove_columns=val_ds.column_names)
    print("train_ds:",train_ds[0])
    if val_ds is not None:
        val_ds = val_ds.map(to_text, batched=True, remove_columns=val_ds.column_names)

    # Add LoRA
    print("[INFO] Adding LoRA adapters...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=64,
        target_modules=[
            "q_proj", "v_proj"],
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=SEED,)

    # Trainer
    print("[INFO] Starting SFTTrainer...")
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_ds,
        eval_dataset=val_ds,

        args=SFTConfig(
            output_dir=OUT_DIR,
            per_device_train_batch_size=PER_DEVICE_BS,
            gradient_accumulation_steps=GRAD_ACCUM,
            max_steps=MAX_STEPS,
            learning_rate=LR,
            warmup_steps=10,
            logging_steps=10,
            eval_strategy="steps" if val_ds is not None else "no",
            eval_steps=50,
            weight_decay=0.01,
            lr_scheduler_type="linear",
            optim="adamw_torch",
            seed=SEED,
            report_to="none",
            bf16=bf16_supported,
            fp16=not bf16_supported,
            packing=False,
            save_strategy="steps",
            save_steps=100,
            dataset_text_field="text",
        ),
    )


    # Early Stopping Next iteration
    """from transformers import EarlyStoppingCallback

    # Add dropout
    model.config.hidden_dropout = 0.1
    model.config.attention_dropout = 0.1
    model.config.dropout = 0.1

    # Add LoRA
    model = FastLanguageModel.get_peft_model(...)

    # Trainer with Early Stopping
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_ds,
        eval_dataset=val_ds,

        args=SFTConfig(
            output_dir=OUT_DIR,
            per_device_train_batch_size=PER_DEVICE_BS,
            gradient_accumulation_steps=GRAD_ACCUM,
            max_steps=MAX_STEPS,
            learning_rate=LR,
            warmup_steps=10,
            logging_steps=10,
            eval_strategy="steps",
            eval_steps=50,
            weight_decay=0.01,
            optim="adamw_torch",
            save_strategy="steps",
            save_steps=100,
            bf16=bf16_supported,
            fp16=not bf16_supported,
            packing=False,
            dataset_text_field="text",
        ),

        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )
    """

    print("[INFO] Training...")
    trainer.train(resume_from_checkpoint=False)

    print("[INFO] Saving LoRA + tokenizer...")

    # saving LoRA adapters + tokenizer
    os.makedirs(OUT_DIR, exist_ok=True)
    model.save_pretrained(OUT_DIR)
    tokenizer.save_pretrained(OUT_DIR)
    print(f"[OK] LoRA adapters and tokenizer saved to: {OUT_DIR}")

    # 9) Merge + convert to GGUF + create Ollama model (optional)
    if DO_MERGE:
        merged_dir = OUT_DIR + "-merged"
        merged_path = Path(merged_dir)
        if merged_path.exists():
            print(f"[INFO] Removing existing merged dir: {merged_dir}")
            shutil.rmtree(merged_dir)

        print(f"[INFO] Merging adapters into {merged_dir} ...")
        if hasattr(FastLanguageModel, "merge_lora"):
            FastLanguageModel.merge_lora(
                model,
                lora_model_dir=OUT_DIR,
                save_dir=merged_dir,
                dtype=torch.bfloat16,
            )
        else:
            # fallback API
            model.save_pretrained_merged(merged_dir, tokenizer, save_method="merged_16bit")

        # ensure tokenizer.model is present
        ensure_tokenizer_model(tokenizer, merged_path, BASE)


        # CLEAR GPU CACHE AFTER MERGE
        import torch
        torch.cuda.empty_cache()
        print("[INFO] GPU cache cleared after merging adapters.")
        # ensure llama.cpp is present and built
        try:
            ensure_llama_cpp(LLAMACPP_DIR)
        except Exception as e:
            raise RuntimeError(f"Failed to prepare llama.cpp: {e}")

        # find conversion script in llama.cpp repo
        convert_script = LLAMACPP_DIR / "convert-hf-to-gguf.py"
        if not convert_script.exists():
            convert_script = LLAMACPP_DIR / "convert_hf_to_gguf.py"
        if not convert_script.exists():
            raise FileNotFoundError("Could not find convert-hf-to-gguf.py in llama.cpp repository.")

        ggufs = []
        for outtype in QUANTS:
            gguf_out = f"{merged_dir}-{outtype}.gguf"
            cmd = [
                "python3", str(convert_script),
                merged_dir,
                "--outfile", gguf_out,
                "--outtype", outtype,
            ]
            print(f"[INFO] Converting merged HF model to GGUF ({outtype}) -> {gguf_out}")
            subprocess.run(cmd, check=True)
            ggufs.append(gguf_out)

        # Write Modelfile and create an Ollama model
        chosen_gguf = ggufs[-1]  # pick the last quant produced (e.g., q8_0)
        write_modelfile(Path(CUSTOM_MODEFILE), chosen_gguf, Path("Modelfile"))

        model_name = Path(OUT_DIR).name
        print(f"[INFO] Creating Ollama model '{model_name}' from Modelfile (requires 'ollama' CLI)...")
        subprocess.run(["ollama", "create", model_name, "-f", "Modelfile"], check=True)
        print(f"[OK] Ollama model created: {model_name}")

    print("[DONE] Pipeline complete.")


if __name__ == "__main__":
    main()




