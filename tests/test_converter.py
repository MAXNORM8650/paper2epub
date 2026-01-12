"""
Tests for the converter module
"""

import pytest

from paper2epub.converter import Paper2EpubConverter


class TestPaper2EpubConverter:
    """Test suite for Paper2EpubConverter"""

    def test_init_auto_device(self):
        """Test automatic device detection"""
        # NougatModel is lazy loaded, so no mock needed for init
        converter = Paper2EpubConverter(device=None)
        assert converter.device in ["cuda", "mps", "cpu"]

    def test_init_specific_device(self):
        """Test manual device specification"""
        converter = Paper2EpubConverter(device="cpu")
        assert converter.device == "cpu"

    def test_model_tag(self):
        """Test model tag configuration"""
        converter = Paper2EpubConverter(model_tag="0.1.0-base")
        assert converter.model_tag == "0.1.0-base"

    def test_validate_pdf_not_found(self):
        """Test PDF validation with non-existent file"""
        converter = Paper2EpubConverter()
        with pytest.raises(FileNotFoundError):
            converter.extract_pdf_to_markdown("nonexistent.pdf")

    # Add more tests here
