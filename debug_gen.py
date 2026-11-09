#!/usr/bin/env python
"""Debug script to test fine-tuned model generation"""
import sys
sys.path.insert(0, '.')

from app.config import get_settings
from app.services.model_registry import ModelRegistry
import asyncio
import torch

async def main():
    settings = get_settings()
    registry = ModelRegistry(settings)
    await registry.initialize()

    model_info = registry.models['finetuned']
    tokenizer = model_info.tokenizer
    model = model_info.model

    print("=== Tokenizer Info ===")
    print(f"pad_token: {tokenizer.pad_token}")
    print(f"pad_token_id: {tokenizer.pad_token_id}")
    print(f"eos_token: {tokenizer.eos_token}")
    print(f"eos_token_id: {tokenizer.eos_token_id}")
    print(f"unk_token: {tokenizer.unk_token}")
    print(f"unk_token_id: {tokenizer.unk_token_id}")

    print("\n=== Test Generation (with padding=True) ===")
    prompt = "summarize to at most 20%: This is a test article about machine learning and artificial intelligence. The field has grown rapidly in recent years with many breakthroughs in deep learning, natural language processing, and computer vision. Researchers are exploring new architectures and training methods to improve model performance."
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512, padding=True).to("cuda")
    print(f"Input shape: {inputs['input_ids'].shape}")

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=128,
            num_beams=4,
            do_sample=False,
            early_stopping=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    print(f"\nOutput shape: {outputs.shape}")
    print(f"Input length: {inputs['input_ids'].shape[1]}")

    # Decode full sequence (new behavior matching summarizer.py)
    generated_tokens = outputs[0]
    print(f"Generated tokens: {generated_tokens.tolist()}")
    print(f"Generated tokens length: {len(generated_tokens)}")

    decoded = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    print(f'Full decoded (skip_special=True): "{decoded}"')

    # Also show just the new tokens for comparison
    new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
    print(f"\nNew tokens only: {new_tokens.tolist()}")
    print(f"New tokens length: {len(new_tokens)}")
    decoded_new = tokenizer.decode(new_tokens, skip_special_tokens=True)
    print(f'New tokens decoded: "{decoded_new}"')

    print("\n=== Test with minimal generate params (like notebook) ===")
    with torch.inference_mode():
        outputs2 = model.generate(
            **inputs,
            max_new_tokens=128,
            num_beams=4,
            do_sample=False,
        )
    generated_tokens2 = outputs2[0]
    decoded2 = tokenizer.decode(generated_tokens2, skip_special_tokens=True)
    print(f'Full decoded (minimal params): "{decoded2}"')
    new_tokens2 = outputs2[0][inputs["input_ids"].shape[1]:]
    print(f'New tokens only: {new_tokens2.tolist()}')

if __name__ == "__main__":
    asyncio.run(main())