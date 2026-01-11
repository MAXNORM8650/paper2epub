"""
Batch conversion example for paper2epub
"""

from pathlib import Path
from paper2epub import Paper2EpubConverter


def batch_convert(input_dir: str, output_dir: str = "output"):
    """
    Convert all PDFs in a directory to EPUB format.

    Args:
        input_dir: Directory containing PDF files
        output_dir: Directory for output EPUB files
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Initialize converter once (reuse for all files)
    converter = Paper2EpubConverter(model_tag="0.1.0-small")

    # Find all PDF files
    pdf_files = list(input_path.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")

    # Convert each PDF
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Converting: {pdf_file.name}")

        try:
            epub_output = output_path / f"{pdf_file.stem}.epub"
            converter.convert(
                pdf_path=pdf_file,
                output_path=epub_output,
            )
            print(f"✓ Success: {epub_output}")
        except Exception as e:
            print(f"✗ Failed: {e}")
            continue


if __name__ == "__main__":
    # Convert all PDFs in 'papers' directory
    batch_convert("papers", "output")
