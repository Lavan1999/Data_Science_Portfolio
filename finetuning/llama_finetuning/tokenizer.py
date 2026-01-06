
# 1. Extract all unique HS codes from your dataset
def extract_hs_tokens_from_dataset(dataset_path: Path):
    hs_codes = set()

    hs_regex = re.compile(r"\b\d{4}_\d{4}_\d{4}\b")

    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                j = json.loads(line)
            except:
                continue

            for msg in j.get("messages", []):
                if msg.get("role") == "assistant":
                    matches = hs_regex.findall(msg["content"])
                    for m in matches:
                        hs_codes.add(m)

    return sorted(list(hs_codes))


# 2. Rebuild tokenizer.model with HS codes as protected tokens
def rebuild_tokenizer_model_from_json(tokenizer_json_path: Path,
                                      output_path: Path,
                                      hs_tokens: list):
    print("[INFO] Rebuilding tokenizer.model with HS codes protected...")

    tok = Tokenizer.from_file(str(tokenizer_json_path))
    vocab = tok.get_vocab()

    vocab_txt = output_path.with_suffix(".vocab.txt")
    with vocab_txt.open("w", encoding="utf-8") as f:
        for token, idx in sorted(vocab.items(), key=lambda kv: kv[1]):
            f.write(token.replace("\n", " ") + "\n")

    # USER DEFINED TOKENS (HS CODES)
    user_tokens_path = output_path.with_suffix(".hs_tokens.txt")
    with open(user_tokens_path, "w", encoding="utf-8") as f:
        for t in hs_tokens:
            f.write(t + "\n")

    user_token_string = ",".join(hs_tokens)

    sp_model_prefix = str(output_path.with_suffix(""))
    vocab_size = max(len(vocab) + len(hs_tokens), 12000)

    print(f"[INFO] Adding {len(hs_tokens)} HS codes as user-defined tokens...")

    spm.SentencePieceTrainer.Train(
        f"--input={vocab_txt} "
        f"--model_prefix={sp_model_prefix} "
        f"--vocab_size={vocab_size} "
        f"--model_type=bpe "
        f"--character_coverage=1.0 "
        f"--user_defined_symbols={user_token_string}"
    )

    print("[INFO] New tokenizer.model generated successfully.")


# 3. Ensure tokenizer.model exists OR rebuild with HS codes
def ensure_tokenizer_model(tokenizer,
                           merged_dir: Path,
                           base_model_id: str,
                           dataset_for_hs_codes: Path):

    tokenizer.save_pretrained(merged_dir)
    tok_path = merged_dir / "tokenizer.model"
    tok_json = merged_dir / "tokenizer.json"

    if tok_path.exists() and tok_path.stat().st_size > 0:
        print("[INFO] tokenizer.model already exists.")
        return

    print("[WARN] tokenizer.model missing → rebuilding...")

    if not tok_json.exists():
        raise FileNotFoundError("ERROR: tokenizer.json missing; cannot rebuild tokenizer.model")

    # --- Extract all HS code tokens ---
    hs_tokens = extract_hs_tokens_from_dataset(dataset_for_hs_codes)
    print(f"[INFO] Extracted {len(hs_tokens)} HS code tokens from dataset.")

    # --- Build new tokenizer with HS codes protected ---
    rebuild_tokenizer_model_from_json(tok_json, tok_path, hs_tokens)

    if not tok_path.exists():
        raise FileNotFoundError("ERROR: tokenizer.model missing even after rebuild.")

    print("[INFO] tokenizer.model is ready.")




#    ---------------------------------------------------------------

# Entire code combined into a single file: llama_finetuning/tokenizer.py

import json
from pathlib import Path
from tokenizers import Tokenizer
import sentencepiece as spm
import re

# -----------------------------
# Step 1: Extract HS codes from dataset
# -----------------------------
def extract_hs_codes_from_dataset(dataset_path: Path):
    """
    Extract all unique HS codes from 'assistant' messages in the dataset.
    Supports 12-digit numeric or 4_4_4 format.
    """
    hs_regex = re.compile(r"\b\d{12}\b|\d{4}_\d{4}_\d{4}\b")
    hs_tokens = set()

    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                j = json.loads(line)
            except:
                continue
            for msg in j.get("messages", []):
                if msg.get("role") == "assistant":
                    matches = hs_regex.findall(msg.get("content", ""))
                    hs_tokens.update(matches)

    return sorted(list(hs_tokens))

# -----------------------------
# Step 2: Rebuild tokenizer with HS codes as single tokens
# -----------------------------
def rebuild_tokenizer_model_from_json(tokenizer_json_path: Path,
                                      output_path: Path,
                                      hs_tokens: list):
    """
    Rebuilds tokenizer.model from tokenizer.json, adding HS codes as user-defined tokens.
    Each HS code becomes one token ID during training/generation.
    """
    print("[INFO] Rebuilding tokenizer.model ...")
    tok = Tokenizer.from_file(str(tokenizer_json_path))
    vocab = tok.get_vocab()

    # Save vocab to vocab.txt for SentencePiece training
    vocab_txt = output_path.with_suffix(".vocab.txt")
    with vocab_txt.open("w", encoding="utf-8") as f:
        for token, idx in sorted(vocab.items(), key=lambda kv: kv[1]):
            f.write(token.replace("\n", " ") + "\n")

    # User-defined HS codes
    user_token_string = ",".join(hs_tokens)
    sp_model_prefix = str(output_path.with_suffix(""))
    vocab_size = max(len(vocab) + len(hs_tokens), 12000)

    print(f"[INFO] Adding {len(hs_tokens)} HS codes as user-defined tokens...")

    spm.SentencePieceTrainer.Train(
        f"--input={vocab_txt} "
        f"--model_prefix={sp_model_prefix} "
        f"--vocab_size={vocab_size} "
        f"--model_type=bpe "
        f"--character_coverage=1.0 "
        f"--user_defined_symbols={user_token_string}"
    )

    print("[INFO] New tokenizer.model generated successfully.")

# -----------------------------
# Step 3: Ensure tokenizer.model exists or rebuild
# -----------------------------
def ensure_tokenizer_model(tokenizer, merged_dir: Path, dataset_path: Path):
    """
    Save tokenizer, rebuild tokenizer.model if missing, and add HS codes automatically.
    """
    tokenizer.save_pretrained(merged_dir)
    tok_path = merged_dir / "tokenizer.model"
    tok_json = merged_dir / "tokenizer.json"

    if tok_path.exists() and tok_path.stat().st_size > 0:
        print("[INFO] tokenizer.model already exists.")
        return

    if not tok_json.exists():
        raise FileNotFoundError("ERROR: tokenizer.json missing; cannot rebuild tokenizer.model")

    # Step 1: Extract HS codes from dataset
    hs_tokens = extract_hs_codes_from_dataset(dataset_path)
    print(f"[INFO] Extracted {len(hs_tokens)} HS code tokens from dataset.")

    # Step 2: Rebuild tokenizer.model
    rebuild_tokenizer_model_from_json(tok_json, tok_path, hs_tokens)

    if not tok_path.exists():
        raise FileNotFoundError("ERROR: tokenizer.model missing even after rebuild.")

    print("[INFO] tokenizer.model is ready with HS codes as single tokens.")

# -----------------------------
# Step 4: Example usage
# -----------------------------
if __name__ == "__main__":
    from transformers import AutoTokenizer

    dataset_path = Path("/home/ubuntu/Llama_3.1_finetuning/llama_finetuning/json/train.jsonl")
    merged_dir = Path("/home/ubuntu/Llama_3.1_finetuning/llama_finetuning/merged_tokenizer")

    tokenizer = AutoTokenizer.from_pretrained("/home/ubuntu/Llama_3.1_finetuning/llama_finetuning/base_tokenizer")

    ensure_tokenizer_model(tokenizer, merged_dir, dataset_path)

    # Test encoding/decoding
    test_hs = "0106_3990_0001"
    encoded = tokenizer.encode(test_hs)
    print("Encoded:", encoded)

    decoded = tokenizer.decode(encoded)
    print("Decoded:", decoded)
