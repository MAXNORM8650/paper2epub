"""
Test script to verify the converter works correctly
"""

import sys
from pathlib import Path
from paper2epub import Paper2EpubConverter


def test_converter():
    """Test the converter initialization and basic functionality."""

    print("=" * 60)
    print("Testing paper2epub Converter")
    print("=" * 60)

    # Test 1: Initialize converter
    print("\n1. Initializing converter...")
    try:
        converter = Paper2EpubConverter(
            model_tag="0.1.0-small",
            device="cpu",  # Use CPU for testing
        )
        print(f"   ✓ Success - Device: {converter.device}, Model: {converter.model_tag}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

    # Test 2: Check if model loaded
    print("\n2. Checking model...")
    try:
        assert hasattr(converter, 'model')
        print("   ✓ Model loaded successfully")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

    # Test 3: Try to convert a PDF if one is provided
    if len(sys.argv) > 1:
        pdf_path = Path(sys.argv[1])
        print(f"\n3. Converting PDF: {pdf_path.name}")
        try:
            output = converter.convert(
                pdf_path=pdf_path,
                save_markdown=True,
            )
            print(f"   ✓ Conversion successful!")
            print(f"   Output: {output}")
            print(f"   Markdown: {pdf_path.with_suffix('.md')}")
        except Exception as e:
            print(f"   ✗ Conversion failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print("\n3. Skipping PDF conversion (no file provided)")
        print("   Run: python test_converter.py /path/to/paper.pdf")

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_converter()
    sys.exit(0 if success else 1)
