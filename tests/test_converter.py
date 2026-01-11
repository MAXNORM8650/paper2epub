"""
Tests for the converter module
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from paper2epub.converter import Paper2EpubConverter


class TestPaper2EpubConverter:
    """Test suite for Paper2EpubConverter"""

    @patch("paper2epub.converter.NougatModel")
    def test_init_auto_device(self, mock_model):
        """Test automatic device detection"""
        converter = Paper2EpubConverter(device=None)
        assert converter.device in ["cuda", "mps", "cpu"]

    @patch("paper2epub.converter.NougatModel")
    def test_init_specific_device(self, mock_model):
        """Test manual device specification"""
        converter = Paper2EpubConverter(device="cpu")
        assert converter.device == "cpu"

    @patch("paper2epub.converter.NougatModel")
    def test_model_tag(self, mock_model):
        """Test model tag configuration"""
        converter = Paper2EpubConverter(model_tag="0.1.0-base")
        assert converter.model_tag == "0.1.0-base"

    def test_validate_pdf_not_found(self):
        """Test PDF validation with non-existent file"""
        converter = Paper2EpubConverter()
        with pytest.raises(FileNotFoundError):
            converter.extract_pdf_to_markdown("nonexistent.pdf")

    # Add more tests here
