"""
Shared pytest fixtures for paper2epub tests
"""

import io
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from PIL import Image


@pytest.fixture
def sample_pdf_path():
    """Path to test PDF file."""
    return Path(__file__).parent.parent / "inputs" / "deft.pdf"


@pytest.fixture
def sample_image_bytes():
    """Generate sample PNG image bytes."""
    img = Image.new("RGB", (200, 200), color="red")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def small_image_bytes():
    """Generate small PNG image bytes (for filtering tests)."""
    img = Image.new("RGB", (50, 50), color="blue")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def mock_fitz_document(sample_image_bytes):
    """Mock PyMuPDF document for testing."""
    mock_doc = MagicMock()
    mock_doc.__len__ = Mock(return_value=2)

    mock_page = MagicMock()
    mock_page.get_images.return_value = [
        (1, 0, 200, 200, 8, "DeviceRGB", "", "Im1", "FlateDecode", 0)
    ]

    mock_doc.__getitem__ = Mock(return_value=mock_page)
    mock_doc.extract_image.return_value = {
        "image": sample_image_bytes,
        "ext": "png",
    }
    mock_doc.close = Mock()

    return mock_doc


@pytest.fixture
def mock_nougat_model():
    """Mock Nougat model to avoid loading in CI."""
    with patch("nougat.NougatModel") as mock_model_class:
        mock_instance = MagicMock()
        mock_instance.eval.return_value = None
        mock_instance.to.return_value = mock_instance
        mock_instance.inference.return_value = {
            "predictions": ["# Test Title\n\nTest content with Figure 1."]
        }
        mock_instance.encoder.prepare_input = MagicMock(return_value=MagicMock())
        mock_model_class.from_pretrained.return_value = mock_instance
        yield mock_model_class


@pytest.fixture
def mock_checkpoint():
    """Mock checkpoint retrieval."""
    with patch("nougat.utils.checkpoint.get_checkpoint") as mock:
        mock.return_value = "/fake/checkpoint/path"
        yield mock


@pytest.fixture
def mock_lazy_dataset():
    """Mock LazyDataset for testing."""
    with patch("nougat.utils.dataset.LazyDataset") as mock:
        mock_instance = MagicMock()
        mock_instance.__len__ = Mock(return_value=1)
        mock_instance.__getitem__ = Mock(return_value=(MagicMock(), None))
        mock.return_value = mock_instance
        yield mock
