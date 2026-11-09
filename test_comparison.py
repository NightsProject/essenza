#!/usr/bin/env python
"""Test script to compare baseline vs finetuned summaries on different paragraphs."""

import asyncio
from app.services.model_registry import ModelRegistry
from app.services.summarizer import Summarizer
from app.services.metrics import MetricsService
from app.config import get_settings

TEST_PARAGRAPHS = [
    (
        "Short technical paragraph",
        "Transformers use self-attention mechanisms to process sequences in parallel, unlike RNNs which process tokens sequentially. This parallelization enables faster training on modern GPUs and allows models to capture long-range dependencies more effectively."
    ),
    (
        "Medium article excerpt",
        "The rise of large language models has transformed natural language processing. Models like GPT, BERT, and T5 demonstrate remarkable capabilities across diverse tasks including translation, summarization, question answering, and code generation. These models are pre-trained on massive text corpora using self-supervised objectives, then fine-tuned for specific downstream tasks. The scaling laws observed by Kaplan et al. suggest that performance improves predictably with model size, dataset size, and compute budget. However, training such models requires substantial computational resources and raises concerns about environmental impact, bias amplification, and potential misuse."
    ),
    (
        "Longer technical article",
        "Fine-tuning pre-trained language models involves adapting the model weights to a specific task or domain using a smaller labeled dataset. Common approaches include full fine-tuning, where all parameters are updated, and parameter-efficient methods like LoRA (Low-Rank Adaptation), which injects trainable low-rank matrices into frozen model layers. LoRA dramatically reduces the number of trainable parameters — often by 10,000x — while maintaining comparable performance to full fine-tuning. This enables fine-tuning on consumer hardware and rapid iteration. The adapter weights can be merged back into the base model for deployment without added inference latency. Recent work explores combining multiple LoRA adapters for multi-task learning and dynamic adapter selection at inference time."
    ),
    (
        "News-style paragraph",
        "Researchers at a leading AI lab announced a breakthrough in efficient model training. Their new technique reduces memory requirements by 40% while maintaining model quality. The method uses gradient checkpointing combined with a novel optimizer that adapts learning rates per layer. Early benchmarks show the approach matches baseline performance on standard NLP tasks including GLUE and SuperGLUE. The team plans to release their implementation open-source next month. Industry experts note this could democratize large model training for smaller organizations and academic labs."
    ),
]


async def run_comparison():
    settings = get_settings()
    registry = ModelRegistry(settings)
    await registry.initialize()

    summarizer = Summarizer(registry, settings)
    metrics = MetricsService()

    thresholds = [10, 20, 30]

    # Get all loaded model IDs dynamically
    loaded_model_ids = [mid for mid, info in registry.models.items() if info.loaded]
    print(f"Loaded models: {loaded_model_ids}")

    for para_name, source_text in TEST_PARAGRAPHS:
        print(f"\n{'='*80}")
        print(f"TEST: {para_name}")
        print(f"Source ({metrics.count_words(source_text)} words): {source_text[:100]}...")
        print(f"{'='*80}")

        for threshold in thresholds:
            print(f"\n  --- Threshold: {threshold}% ---")

            for model_id in loaded_model_ids:
                try:
                    result = await summarizer.summarize(source_text, threshold, model_id)
                    source_wc = metrics.count_words(source_text)
                    summary_wc = metrics.count_words(result.summary)
                    actual_compression = metrics.compression_ratio(source_wc, summary_wc)
                    within_limit = metrics.within_cap(actual_compression, threshold)

                    model_label = registry.get_model_info(model_id).get("label", model_id)
                    print(f"    {model_label}:")
                    print(f"      Summary: {result.summary}")
                    print(f"      Words: {summary_wc} (target ≤{threshold}% = {source_wc * threshold // 100})")
                    print(f"      Compression: {actual_compression:.1f}% {'✓' if within_limit else '✗ OVER'}")

                except Exception as e:
                    print(f"    {model_id}: ERROR - {e}")

    await registry.shutdown()
    print("\n\nDone.")


if __name__ == "__main__":
    asyncio.run(run_comparison())