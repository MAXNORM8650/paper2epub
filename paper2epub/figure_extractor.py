"""
Figure extraction module using PyMuPDF for PDF image extraction
"""

import io
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import fitz  # PyMuPDF
from PIL import Image

logger = logging.getLogger(__name__)


class FigureExtractor:
    """
    Extracts figures/images from PDF files using PyMuPDF.
    """

    def __init__(
        self,
        min_width: int = 100,
        min_height: int = 100,
        output_format: str = "PNG",
        quality: int = 95,
    ):
        """
        Initialize figure extractor.

        Args:
            min_width: Minimum image width to extract (filters tiny icons)
            min_height: Minimum image height to extract
            output_format: Output format for images (PNG, JPEG)
            quality: JPEG quality (1-100) if using JPEG format
        """
        self.min_width = min_width
        self.min_height = min_height
        self.output_format = output_format.upper()
        self.quality = quality

    def extract_images(self, pdf_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Extract all images from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of dicts with keys: 'page', 'index', 'image_bytes',
            'width', 'height', 'format', 'xref'
        """
        pdf_path = Path(pdf_path)
        images = []

        doc = fitz.open(str(pdf_path))

        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)

            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]  # Image xref

                try:
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    # Convert to PIL for processing
                    pil_image = Image.open(io.BytesIO(image_bytes))
                    width, height = pil_image.size

                    # Filter small images (icons, decorations)
                    if width < self.min_width or height < self.min_height:
                        logger.debug(
                            f"Skipping small image on page {page_num + 1}: "
                            f"{width}x{height}"
                        )
                        continue

                    # Convert to target format if needed
                    output_bytes = self._convert_image(pil_image)

                    images.append(
                        {
                            "page": page_num + 1,
                            "index": img_index,
                            "image_bytes": output_bytes,
                            "width": width,
                            "height": height,
                            "format": self.output_format.lower(),
                            "xref": xref,
                            "original_format": image_ext,
                        }
                    )

                    logger.debug(
                        f"Extracted image {img_index} from page {page_num + 1}: "
                        f"{width}x{height} ({image_ext})"
                    )

                except Exception as e:
                    logger.warning(
                        f"Failed to extract image {img_index} from page "
                        f"{page_num + 1}: {e}"
                    )
                    continue

        doc.close()
        logger.info(f"Extracted {len(images)} figures from {pdf_path.name}")
        return images

    def _convert_image(self, pil_image: Image.Image) -> bytes:
        """Convert PIL image to target format bytes."""
        output = io.BytesIO()

        if self.output_format == "JPEG":
            # Convert RGBA to RGB for JPEG
            if pil_image.mode in ("RGBA", "P"):
                pil_image = pil_image.convert("RGB")
            pil_image.save(output, format="JPEG", quality=self.quality)
        else:
            pil_image.save(output, format="PNG")

        return output.getvalue()


class FigureMatcher:
    """
    Matches extracted figures with figure references in markdown content.
    """

    # Regex patterns for figure references in Nougat's markdown output
    FIGURE_PATTERNS = [
        r"Figure\s+(\d+)",
        r"Fig\.\s*(\d+)",
        r"FIG\.\s*(\d+)",
        r"\[Figure\s+(\d+)\]",
        r"!\[.*?Figure\s+(\d+).*?\]",
    ]

    def __init__(self):
        self.compiled_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.FIGURE_PATTERNS
        ]

    def find_figure_references(self, markdown: str) -> List[Dict[str, Any]]:
        """
        Find all figure references in markdown text.

        Args:
            markdown: Markdown content to search

        Returns:
            List of dicts with keys: 'figure_num', 'position', 'match_text'
        """
        references = []

        for pattern in self.compiled_patterns:
            for match in pattern.finditer(markdown):
                references.append(
                    {
                        "figure_num": int(match.group(1)),
                        "position": match.start(),
                        "match_text": match.group(0),
                    }
                )

        # Sort by position and deduplicate by position
        references.sort(key=lambda x: x["position"])
        seen_positions = set()
        deduplicated = []
        for ref in references:
            if ref["position"] not in seen_positions:
                seen_positions.add(ref["position"])
                deduplicated.append(ref)
        return deduplicated

    def insert_images_into_markdown(
        self,
        markdown: str,
        images: List[Dict[str, Any]],
        image_path_prefix: str = "images/",
    ) -> Tuple[str, List[Tuple[str, bytes]]]:
        """
        Insert image references into markdown at appropriate positions.

        Args:
            markdown: Original markdown content
            images: List of extracted image dictionaries
            image_path_prefix: Prefix for image paths in markdown

        Returns:
            Tuple of (modified_markdown, list of (filename, bytes) tuples)
        """
        image_files: List[Tuple[str, bytes]] = []
        insertions = []

        # Group images by page for sequential assignment
        page_images: Dict[int, List[Dict[str, Any]]] = {}
        for img in images:
            page = img["page"]
            if page not in page_images:
                page_images[page] = []
            page_images[page].append(img)

        # Assign figure numbers sequentially
        figure_num = 1
        for page in sorted(page_images.keys()):
            for img in page_images[page]:
                filename = f"figure_{figure_num:03d}.{img['format']}"
                image_files.append((filename, img["image_bytes"]))

                insertions.append(
                    {
                        "figure_num": figure_num,
                        "filename": filename,
                        "page": page,
                    }
                )
                figure_num += 1

        # Add images section at the end of the document
        if insertions:
            image_markdown = "\n\n## Figures\n\n"
            for ins in insertions:
                image_markdown += (
                    f"![Figure {ins['figure_num']}]"
                    f"({image_path_prefix}{ins['filename']})\n\n"
                )

            modified_markdown = markdown + image_markdown
        else:
            modified_markdown = markdown

        return modified_markdown, image_files
