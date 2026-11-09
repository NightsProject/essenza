# app/services/summarizer.py — Tokenization, generation, decoding

import logging
from typing import Literal

import torch
from transformers import PreTrainedTokenizerBase

from app.config import Settings
from app.services.model_registry import ModelRegistry, ModelInfo

logger = logging.getLogger("essenza.summarizer")


class SummarizationResult:
    def __init__(self, summary: str, token_count: int):
        self.summary = summary
        self.token_count = token_count


class Summarizer:
    """
    Orchestrates summarization: prompt building, tokenization, generation, decoding.

    Uses deterministic generation (beam search, no sampling) for reproducible demos.
    """

    def __init__(self, model_registry: ModelRegistry, settings: Settings):
        self.model_registry = model_registry
        self.settings = settings

    def _build_prompt(self, source_text: str, max_compression_percent: int) -> str:
        """Build prompt matching notebook format: 'summarize to at most N%: [source]'"""
        return self.settings.prompt_template.format(
            percent=max_compression_percent,
            text=source_text.strip(),
        )

    def _validate_token_length(self, tokenizer: PreTrainedTokenizerBase, prompt: str) -> int:
        """Validate input doesn't exceed token limit. Returns token count."""
        tokens = tokenizer.encode(prompt, add_special_tokens=True)
        token_count = len(tokens)

        if token_count > self.settings.max_input_tokens:
            raise ValueError(
                f"Input exceeds maximum token limit: {token_count} tokens "
                f"(max {self.settings.max_input_tokens}). "
                f"Please shorten the source text."
            )

        return token_count

    async def summarize(
        self,
        source_text: str,
        max_compression_percent: int,
        model_id: Literal["baseline", "finetuned"],
    ) -> SummarizationResult:
        """Generate summary for given source text and model."""

        # Get model info
        info = self.model_registry.get_model(model_id)

        if not info.loaded:
            raise RuntimeError(f"Model {model_id} not loaded")

        tokenizer = info.tokenizer
        model = info.model
        device = info.device

        # Build prompt
        prompt = self._build_prompt(source_text, max_compression_percent)

        # Validate token length
        self._validate_token_length(tokenizer, prompt)

        # Tokenize
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=False,  # We validated above
            padding=True,
        ).to(device)

        # Generate
        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=self.settings.max_output_tokens,
                num_beams=self.settings.num_beams,
                do_sample=self.settings.do_sample,
                temperature=self.settings.temperature if self.settings.do_sample else None,
                early_stopping=True,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        # Decode generated sequence
        generated_tokens = outputs[0]

        summary = tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True
        ).strip()

        token_count = len(generated_tokens)

        logger.debug(
            "Generated summary for %s: %d tokens, %d chars",
            model_id,
            token_count,
            len(summary),
        )

        return SummarizationResult(
            summary=summary,
            token_count=token_count
        )