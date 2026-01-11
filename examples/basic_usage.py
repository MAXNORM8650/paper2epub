"""
Basic usage example for paper2epub
"""

from paper2epub import Paper2EpubConverter


def main():
    # Initialize converter
    converter = Paper2EpubConverter(
        model_tag="0.1.0-small",  # Use small model for faster processing
        device="auto",             # Auto-detect best device (GPU/MPS/CPU)
    )

    # Convert a single PDF
    output_path = converter.convert(
        pdf_path="sample_paper.pdf",
        title="Sample Academic Paper",
        author="John Doe",
        save_markdown=True,  # Also save the intermediate markdown
    )

    print(f"Conversion complete! Output: {output_path}")


if __name__ == "__main__":
    main()
