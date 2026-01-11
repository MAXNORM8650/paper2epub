"""
Advanced usage example with custom settings
"""

from paper2epub import Paper2EpubConverter
from paper2epub.utils import get_device_info, extract_metadata_from_filename
from pathlib import Path


def advanced_convert():
    # Check available devices
    device_info = get_device_info()
    print("Available devices:")
    print(f"  CUDA: {device_info['cuda_available']}")
    print(f"  MPS (Apple Silicon): {device_info['mps_available']}")
    print(f"  CPU: {device_info['cpu_available']}")

    # Use the base model for better quality (larger, slower)
    converter = Paper2EpubConverter(
        model_tag="0.1.0-base",  # Better quality
        device="auto",
        batch_size=2,  # Process 2 pages at once if GPU available
    )

    pdf_path = Path("complex_paper.pdf")

    # Try to extract metadata from filename
    metadata = extract_metadata_from_filename(pdf_path.name)
    print(f"\nExtracted metadata:")
    print(f"  Title: {metadata['title']}")
    print(f"  Author: {metadata['author']}")

    # Convert with extracted metadata
    output_path = converter.convert(
        pdf_path=pdf_path,
        title=metadata["title"],
        author=metadata["author"],
        language="en",
        save_markdown=True,
    )

    print(f"\nConversion complete!")
    print(f"EPUB: {output_path}")
    print(f"Markdown: {pdf_path.with_suffix('.md')}")


if __name__ == "__main__":
    advanced_convert()
