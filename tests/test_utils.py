"""
Tests for utility functions
"""

import pytest
from pathlib import Path

from paper2epub.utils import (
    validate_pdf,
    ensure_output_path,
    format_file_size,
    extract_metadata_from_filename,
)


class TestUtils:
    """Test suite for utility functions"""

    def test_format_file_size(self):
        """Test file size formatting"""
        assert format_file_size(500) == "500.0 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"

    def test_extract_metadata_simple(self):
        """Test metadata extraction from simple filename"""
        metadata = extract_metadata_from_filename("paper.pdf")
        assert metadata["title"] == "paper"
        assert metadata["author"] == "Unknown"

    def test_extract_metadata_with_author(self):
        """Test metadata extraction with author in filename"""
        metadata = extract_metadata_from_filename("John Doe - Research Paper.pdf")
        assert metadata["title"] == "Research Paper"
        assert metadata["author"] == "John Doe"

    def test_validate_pdf_not_pdf(self):
        """Test validation of non-PDF file"""
        with pytest.raises(ValueError):
            validate_pdf("document.txt")

    def test_ensure_output_path(self, tmp_path):
        """Test output path generation"""
        input_path = tmp_path / "paper.pdf"
        output_path = ensure_output_path(input_path)
        assert output_path.suffix == ".epub"
        assert output_path.stem == "paper"
