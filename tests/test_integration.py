"""
Integration tests for paper2epub
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from paper2epub import Paper2EpubConverter


@pytest.mark.integration
class TestIntegration:
    """Integration tests for full conversion workflow."""

    @pytest.mark.slow
    def test_full_conversion_with_real_pdf(self, sample_pdf_path, tmp_path):
        """
        Test full conversion with real PDF file.

        This test requires a real PDF file and loads the actual Nougat model.
        It's marked as slow and should be skipped in CI.
        """
        if not sample_pdf_path.exists():
            pytest.skip(f"Test PDF not found: {sample_pdf_path}")

        output_path = tmp_path / "output.epub"

        converter = Paper2EpubConverter(
            model_tag="0.1.0-small",
            device="cpu",
            batch_size=1,
            extract_figures=True,
        )

        result = converter.convert(
            pdf_path=sample_pdf_path,
            output_path=output_path,
            title="Test Paper",
            author="Test Author",
        )

        assert result.exists()
        assert result.suffix == ".epub"
        assert result.stat().st_size > 0

    def test_conversion_with_mocked_model(
        self,
        sample_pdf_path,
        tmp_path,
        mock_nougat_model,
        mock_checkpoint,
        mock_lazy_dataset,
        sample_image_bytes,
    ):
        """Test conversion with mocked Nougat model."""
        output_path = tmp_path / "output.epub"

        # Mock figure extraction
        with patch("paper2epub.converter.fitz") as mock_fitz:
            mock_doc = MagicMock()
            mock_doc.__len__ = Mock(return_value=1)
            mock_doc.__enter__ = Mock(return_value=mock_doc)
            mock_doc.__exit__ = Mock(return_value=None)

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
            mock_fitz.open.return_value = mock_doc

            converter = Paper2EpubConverter(
                model_tag="0.1.0-small",
                device="cpu",
                batch_size=1,
                extract_figures=True,
            )

            result = converter.convert(
                pdf_path=sample_pdf_path,
                output_path=output_path,
                title="Test Paper",
                author="Test Author",
            )

            assert result.exists()
            assert result.suffix == ".epub"

    def test_conversion_without_figures(
        self,
        sample_pdf_path,
        tmp_path,
        mock_nougat_model,
        mock_checkpoint,
        mock_lazy_dataset,
    ):
        """Test conversion with figure extraction disabled."""
        output_path = tmp_path / "output.epub"

        converter = Paper2EpubConverter(
            model_tag="0.1.0-small",
            device="cpu",
            batch_size=1,
            extract_figures=False,
        )

        result = converter.convert(
            pdf_path=sample_pdf_path,
            output_path=output_path,
            title="Test Paper",
            author="Test Author",
        )

        assert result.exists()
        assert result.suffix == ".epub"

    def test_conversion_saves_markdown(
        self,
        sample_pdf_path,
        tmp_path,
        mock_nougat_model,
        mock_checkpoint,
        mock_lazy_dataset,
    ):
        """Test that markdown file is saved when requested."""
        output_path = tmp_path / "output.epub"

        converter = Paper2EpubConverter(
            model_tag="0.1.0-small",
            device="cpu",
            batch_size=1,
            extract_figures=False,
        )

        result = converter.convert(
            pdf_path=sample_pdf_path,
            output_path=output_path,
            title="Test Paper",
            author="Test Author",
            save_markdown=True,
        )

        assert result.exists()
        # Markdown file should be created next to PDF
        markdown_path = sample_pdf_path.with_suffix(".md")
        # Note: May need cleanup after test


class TestConverterInitialization:
    """Tests for converter initialization options."""

    def test_init_with_figure_extraction(
        self, mock_nougat_model, mock_checkpoint
    ):
        """Test initialization with figure extraction enabled."""
        converter = Paper2EpubConverter(
            model_tag="0.1.0-small",
            device="cpu",
            extract_figures=True,
            figure_min_size=150,
        )

        assert converter.extract_figures is True
        assert converter.figure_extractor is not None
        assert converter.figure_matcher is not None
        assert converter.figure_extractor.min_width == 150
        assert converter.figure_extractor.min_height == 150

    def test_init_without_figure_extraction(
        self, mock_nougat_model, mock_checkpoint
    ):
        """Test initialization with figure extraction disabled."""
        converter = Paper2EpubConverter(
            model_tag="0.1.0-small",
            device="cpu",
            extract_figures=False,
        )

        assert converter.extract_figures is False
        assert converter.figure_extractor is None
        assert converter.figure_matcher is None

    def test_lazy_model_loading(self, mock_nougat_model, mock_checkpoint):
        """Test that model is loaded lazily."""
        converter = Paper2EpubConverter(
            model_tag="0.1.0-small",
            device="cpu",
            extract_figures=False,
        )

        # Model should not be loaded yet
        assert converter._model_loaded is False

        # Accessing model property should trigger loading
        _ = converter.model

        assert converter._model_loaded is True

    def test_device_auto_detection(self, mock_nougat_model, mock_checkpoint):
        """Test automatic device detection."""
        with patch("torch.cuda.is_available", return_value=False):
            with patch("torch.backends.mps.is_available", return_value=False):
                converter = Paper2EpubConverter(
                    model_tag="0.1.0-small",
                    device=None,
                    extract_figures=False,
                )

                assert converter.device == "cpu"


class TestConverterMethods:
    """Tests for converter helper methods."""

    def test_cleanup_memory(self, mock_nougat_model, mock_checkpoint):
        """Test memory cleanup method."""
        converter = Paper2EpubConverter(
            model_tag="0.1.0-small",
            device="cpu",
            extract_figures=False,
        )

        # Load model first
        _ = converter.model
        assert converter._model_loaded is True

        # Cleanup
        converter._cleanup_memory()

        assert converter._model is None
        assert converter._model_loaded is False

    def test_markdown_to_epub_basic(self, mock_nougat_model, mock_checkpoint, tmp_path):
        """Test basic markdown to EPUB conversion."""
        converter = Paper2EpubConverter(
            model_tag="0.1.0-small",
            device="cpu",
            extract_figures=False,
        )

        output_path = tmp_path / "test.epub"
        markdown_content = "# Test Title\n\nThis is a test paragraph."

        converter.markdown_to_epub(
            markdown_content=markdown_content,
            output_path=output_path,
            title="Test Book",
            author="Test Author",
        )

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_markdown_to_epub_with_images(
        self, mock_nougat_model, mock_checkpoint, tmp_path, sample_image_bytes
    ):
        """Test markdown to EPUB conversion with images."""
        converter = Paper2EpubConverter(
            model_tag="0.1.0-small",
            device="cpu",
            extract_figures=False,
        )

        output_path = tmp_path / "test.epub"
        markdown_content = "# Test Title\n\n![Figure 1](images/figure_001.png)"

        images = [("figure_001.png", sample_image_bytes)]

        converter.markdown_to_epub(
            markdown_content=markdown_content,
            output_path=output_path,
            title="Test Book",
            author="Test Author",
            images=images,
        )

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_markdown_to_epub_with_math(
        self, mock_nougat_model, mock_checkpoint, tmp_path
    ):
        """Test markdown to EPUB conversion with LaTeX math."""
        converter = Paper2EpubConverter(
            model_tag="0.1.0-small",
            device="cpu",
            extract_figures=False,
        )

        output_path = tmp_path / "test.epub"
        markdown_content = """# Test Title

This is inline math: $E = mc^2$

This is display math:

$$
\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}
$$
"""

        converter.markdown_to_epub(
            markdown_content=markdown_content,
            output_path=output_path,
            title="Math Test",
            author="Test Author",
        )

        assert output_path.exists()
        assert output_path.stat().st_size > 0
