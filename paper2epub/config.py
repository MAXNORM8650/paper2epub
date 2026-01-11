"""
Configuration settings for paper2epub
"""

from pathlib import Path
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG: Dict[str, Any] = {
    "model": {
        "default_tag": "0.1.0-small",
        "available_tags": ["0.1.0-small", "0.1.0-base"],
        "batch_size": 1,
    },
    "device": {
        "auto_detect": True,
        "fallback": "cpu",
    },
    "epub": {
        "default_language": "en",
        "include_mathjax": True,
        "css_style": "default",
    },
    "processing": {
        "save_intermediate": False,
        "cleanup_temp": True,
    },
}

# Supported file extensions
SUPPORTED_INPUT_FORMATS = [".pdf"]
SUPPORTED_OUTPUT_FORMATS = [".epub", ".md"]

# Model download URLs (Nougat models)
MODEL_URLS = {
    "0.1.0-small": "facebook/nougat-small",
    "0.1.0-base": "facebook/nougat-base",
}

# Cache directory
CACHE_DIR = Path.home() / ".cache" / "paper2epub"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
