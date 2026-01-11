"""
Utility functions for paper2epub
"""

import logging
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)


def validate_pdf(pdf_path: Union[str, Path]) -> Path:
    """
    Validate that a PDF file exists and is readable.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Validated Path object

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a PDF
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"File is not a PDF: {pdf_path}")

    return pdf_path


def ensure_output_path(
    input_path: Path,
    output_path: Optional[Union[str, Path]] = None,
    suffix: str = ".epub",
) -> Path:
    """
    Ensure output path is valid and create parent directories.

    Args:
        input_path: Input file path
        output_path: Desired output path (or None)
        suffix: File suffix for output

    Returns:
        Validated output path
    """
    if output_path is None:
        output_path = input_path.with_suffix(suffix)
    else:
        output_path = Path(output_path)

    # Create parent directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    return output_path


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def extract_metadata_from_filename(filename: str) -> dict:
    """
    Try to extract metadata from filename.

    Args:
        filename: PDF filename

    Returns:
        Dictionary with extracted metadata
    """
    metadata = {
        "title": Path(filename).stem,
        "author": "Unknown",
    }

    # Simple heuristic: if filename contains " - ", split it
    if " - " in metadata["title"]:
        parts = metadata["title"].split(" - ", 1)
        if len(parts) == 2:
            metadata["author"] = parts[0].strip()
            metadata["title"] = parts[1].strip()

    return metadata


def get_device_info() -> dict:
    """
    Get information about available compute devices.

    Returns:
        Dictionary with device information
    """
    import torch

    info = {
        "cuda_available": torch.cuda.is_available(),
        "mps_available": torch.backends.mps.is_available(),
        "cpu_available": True,
    }

    if info["cuda_available"]:
        info["cuda_device_count"] = torch.cuda.device_count()
        info["cuda_device_name"] = torch.cuda.get_device_name(0)

    return info
