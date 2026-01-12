"""
Tests for figure extraction module
"""

import io
from unittest.mock import MagicMock, Mock, patch

from PIL import Image

from paper2epub.figure_extractor import FigureExtractor, FigureMatcher


class TestFigureExtractor:
    """Tests for FigureExtractor class."""

    def test_init_defaults(self):
        """Test default initialization."""
        extractor = FigureExtractor()
        assert extractor.min_width == 100
        assert extractor.min_height == 100
        assert extractor.output_format == "PNG"
        assert extractor.quality == 95

    def test_init_custom(self):
        """Test custom initialization."""
        extractor = FigureExtractor(
            min_width=50,
            min_height=50,
            output_format="JPEG",
            quality=80,
        )
        assert extractor.min_width == 50
        assert extractor.min_height == 50
        assert extractor.output_format == "JPEG"
        assert extractor.quality == 80

    @patch("paper2epub.figure_extractor.fitz")
    def test_extract_images(self, mock_fitz, sample_image_bytes):
        """Test image extraction from PDF."""
        # Setup mock document
        mock_doc = MagicMock()
        mock_doc.__len__ = Mock(return_value=1)

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

        extractor = FigureExtractor()
        images = extractor.extract_images("test.pdf")

        assert len(images) == 1
        assert images[0]["page"] == 1
        assert "image_bytes" in images[0]
        assert images[0]["width"] == 200
        assert images[0]["height"] == 200

    @patch("paper2epub.figure_extractor.fitz")
    def test_filter_small_images(self, mock_fitz, small_image_bytes):
        """Test that small images are filtered out."""
        mock_doc = MagicMock()
        mock_doc.__len__ = Mock(return_value=1)

        mock_page = MagicMock()
        mock_page.get_images.return_value = [
            (1, 0, 50, 50, 8, "DeviceRGB", "", "Im1", "FlateDecode", 0)
        ]

        mock_doc.__getitem__ = Mock(return_value=mock_page)
        mock_doc.extract_image.return_value = {
            "image": small_image_bytes,
            "ext": "png",
        }
        mock_doc.close = Mock()
        mock_fitz.open.return_value = mock_doc

        extractor = FigureExtractor(min_width=100, min_height=100)
        images = extractor.extract_images("test.pdf")

        assert len(images) == 0  # Small image should be filtered

    def test_convert_image_png(self, sample_image_bytes):
        """Test PNG image conversion."""
        extractor = FigureExtractor(output_format="PNG")
        img = Image.open(io.BytesIO(sample_image_bytes))
        result = extractor._convert_image(img)

        assert result is not None
        assert len(result) > 0
        # Verify it's valid PNG
        result_img = Image.open(io.BytesIO(result))
        assert result_img.format == "PNG"

    def test_convert_image_jpeg(self):
        """Test JPEG conversion from RGBA."""
        extractor = FigureExtractor(output_format="JPEG", quality=85)
        # Create RGBA image
        img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        result = extractor._convert_image(img)

        # Verify it's valid JPEG (RGBA converted to RGB)
        result_img = Image.open(io.BytesIO(result))
        assert result_img.format == "JPEG"
        assert result_img.mode == "RGB"

    @patch("paper2epub.figure_extractor.fitz")
    def test_extract_multiple_pages(self, mock_fitz, sample_image_bytes):
        """Test extraction from multiple pages."""
        mock_doc = MagicMock()
        mock_doc.__len__ = Mock(return_value=3)

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

        extractor = FigureExtractor()
        images = extractor.extract_images("test.pdf")

        # Should have 3 images (one per page)
        assert len(images) == 3
        assert images[0]["page"] == 1
        assert images[1]["page"] == 2
        assert images[2]["page"] == 3


class TestFigureMatcher:
    """Tests for FigureMatcher class."""

    def test_find_figure_references_basic(self):
        """Test finding basic figure references."""
        matcher = FigureMatcher()
        markdown = "As shown in Figure 1, the results are clear. See also Fig. 2."

        refs = matcher.find_figure_references(markdown)

        assert len(refs) == 2
        assert refs[0]["figure_num"] == 1
        assert refs[1]["figure_num"] == 2

    def test_find_figure_references_various_formats(self):
        """Test various figure reference formats."""
        matcher = FigureMatcher()
        markdown = """
        Figure 1 shows results.
        As in Fig. 2 we can see.
        FIG. 3 demonstrates this.
        [Figure 4] is referenced.
        """

        refs = matcher.find_figure_references(markdown)

        figure_nums = [r["figure_num"] for r in refs]
        assert 1 in figure_nums
        assert 2 in figure_nums
        assert 3 in figure_nums
        assert 4 in figure_nums

    def test_find_figure_references_case_insensitive(self):
        """Test case insensitive matching."""
        matcher = FigureMatcher()
        markdown = "FIGURE 1, figure 2, Figure 3, FiGuRe 4"

        refs = matcher.find_figure_references(markdown)

        assert len(refs) >= 4

    def test_find_figure_references_no_matches(self):
        """Test when there are no figure references."""
        matcher = FigureMatcher()
        markdown = "This is a document without any figure references."

        refs = matcher.find_figure_references(markdown)

        assert len(refs) == 0

    def test_insert_images_into_markdown(self, sample_image_bytes):
        """Test image insertion into markdown."""
        matcher = FigureMatcher()
        markdown = "# Test Paper\n\nAs shown in Figure 1."
        images = [
            {
                "page": 1,
                "index": 0,
                "image_bytes": sample_image_bytes,
                "width": 200,
                "height": 200,
                "format": "png",
                "xref": 1,
            }
        ]

        modified_md, image_files = matcher.insert_images_into_markdown(markdown, images)

        assert "## Figures" in modified_md
        assert "![Figure 1]" in modified_md
        assert len(image_files) == 1
        assert image_files[0][0] == "figure_001.png"

    def test_insert_multiple_images(self, sample_image_bytes):
        """Test inserting multiple images."""
        matcher = FigureMatcher()
        markdown = "Content with multiple figures."
        images = [
            {
                "page": 1,
                "index": 0,
                "image_bytes": sample_image_bytes,
                "width": 200,
                "height": 200,
                "format": "png",
                "xref": 1,
            },
            {
                "page": 2,
                "index": 0,
                "image_bytes": sample_image_bytes,
                "width": 300,
                "height": 300,
                "format": "png",
                "xref": 2,
            },
        ]

        modified_md, image_files = matcher.insert_images_into_markdown(markdown, images)

        assert len(image_files) == 2
        assert "figure_001.png" in modified_md
        assert "figure_002.png" in modified_md

    def test_insert_no_images(self):
        """Test when there are no images to insert."""
        matcher = FigureMatcher()
        markdown = "Content without images."
        images = []

        modified_md, image_files = matcher.insert_images_into_markdown(markdown, images)

        assert modified_md == markdown
        assert len(image_files) == 0

    def test_images_sorted_by_page(self, sample_image_bytes):
        """Test that images are sorted by page number."""
        matcher = FigureMatcher()
        markdown = "Content."
        # Images in reverse order
        images = [
            {
                "page": 3,
                "index": 0,
                "image_bytes": sample_image_bytes,
                "width": 200,
                "height": 200,
                "format": "png",
                "xref": 3,
            },
            {
                "page": 1,
                "index": 0,
                "image_bytes": sample_image_bytes,
                "width": 200,
                "height": 200,
                "format": "png",
                "xref": 1,
            },
        ]

        modified_md, image_files = matcher.insert_images_into_markdown(markdown, images)

        # First file should be from page 1
        assert image_files[0][0] == "figure_001.png"
        assert image_files[1][0] == "figure_002.png"
