#!/usr/bin/env python
"""
essenza — Extreme Text Summarization Web Application

Entry point for running the application via `uv run run.py`.
"""

import os
import sys
from pathlib import Path

# Ensure we're in the project root
PROJECT_ROOT = Path(__file__).parent
os.chdir(PROJECT_ROOT)

if __name__ == "__main__":
    import uvicorn
    from app.config import get_settings

    settings = get_settings()

    print(f"Starting {settings.app_name} v{settings.version}")
    print(f"Host: {settings.host}:{settings.port}")
    print(f"Debug: {settings.debug}")
    print(f"Model paths:")
    print(f"  Baseline: {settings.baseline_model_path}")
    print(f"  Fine-tuned: {settings.finetuned_model_path}")
    print(f"Device: {settings.device}")
    print(f"Log level: {settings.log_level}")
    print()

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )