"""
Core converter module using Nougat for academic PDF processing
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Union
import logging

from ebooklib import epub
from PIL import Image
import torch

logger = logging.getLogger(__name__)


class Paper2EpubConverter:
    """
    Main converter class for transforming academic PDFs to EPUB format.
    Uses Nougat (Meta) for PDF extraction with LaTeX math support.
    """

    def __init__(
        self,
        model_tag: str = "0.1.0-small",
        device: Optional[str] = None,
        batch_size: int = 1,
    ):
        """
        Initialize the converter.

        Args:
            model_tag: Nougat model version ('0.1.0-small', '0.1.0-base')
            device: Device to run on ('cuda', 'mps', 'cpu', or None for auto-detect)
            batch_size: Batch size for processing pages
        """
        self.model_tag = model_tag
        self.batch_size = batch_size

        # Auto-detect device if not specified
        if device is None:
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"  # Apple Silicon
            else:
                self.device = "cpu"
        else:
            self.device = device

        logger.info(f"Initializing Paper2Epub converter with device: {self.device}")
        self._load_model()

    def _load_model(self):
        """Load Nougat model lazily."""
        try:
            from nougat import NougatModel
            from nougat.utils.checkpoint import get_checkpoint

            checkpoint = get_checkpoint(None, model_tag=self.model_tag)
            self.model = NougatModel.from_pretrained(checkpoint)
            self.model = self.model.to(self.device)
            self.model.eval()
            logger.info(f"Nougat model '{self.model_tag}' loaded successfully")
        except ImportError as e:
            logger.error("Nougat not installed. Run: pip install nougat-ocr")
            raise ImportError(
                "nougat-ocr is required. Install with: pip install nougat-ocr"
            ) from e
        except Exception as e:
            logger.error(f"Failed to load Nougat model: {e}")
            raise

    def extract_pdf_to_markdown(self, pdf_path: Union[str, Path]) -> str:
        """
        Extract PDF content to Markdown using Nougat.

        Args:
            pdf_path: Path to input PDF file

        Returns:
            Extracted markdown content with LaTeX equations
        """
        from nougat.utils.dataset import LazyDataset
        from nougat.postprocessing import markdown_compatible
        from nougat.dataset.rasterize import rasterize_paper

        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.info(f"Extracting content from: {pdf_path.name}")

        try:
            # Create dataset with the correct API
            dataset = LazyDataset(
                str(pdf_path),
                prepare=rasterize_paper,
            )

            # Process PDF page by page
            markdown_content = []

            # Process each page individually to avoid batching issues
            for idx in range(len(dataset)):
                try:
                    image, _ = dataset[idx]

                    if image is None:
                        logger.warning(f"Skipping page {idx + 1} (failed to render)")
                        continue

                    # Debug: Log what we actually received
                    logger.debug(f"Page {idx + 1} - Image type: {type(image)}")

                    # Handle case where rasterize_paper returns list of images
                    if isinstance(image, (list, tuple)):
                        logger.debug(f"Page {idx + 1} - Got list/tuple with {len(image)} items")
                        if len(image) == 0:
                            logger.warning(f"Skipping page {idx + 1} (empty image list)")
                            continue
                        # Extract first image
                        image = image[0]
                        logger.debug(f"Page {idx + 1} - Extracted image type: {type(image)}")

                    # Nougat's inference can accept PIL images directly
                    # So we pass it as-is without tensor conversion
                    with torch.no_grad():
                        outputs = self.model.inference(
                            image=image,  # Pass PIL image directly
                            return_attentions=False,
                        )

                    for output in outputs:
                        # Post-process markdown
                        markdown = markdown_compatible(output)
                        markdown_content.append(markdown)

                    logger.info(f"Processed page {idx + 1}/{len(dataset)}")

                except Exception as e:
                    logger.error(f"Failed to process page {idx + 1}: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())
                    continue

            if not markdown_content:
                raise ValueError("No content extracted from PDF")

            full_markdown = "\n\n".join(markdown_content)
            return full_markdown

        except Exception as e:
            logger.error(f"Failed to extract PDF: {e}")
            raise

    def markdown_to_epub(
        self,
        markdown_content: str,
        output_path: Union[str, Path],
        title: str = "Academic Paper",
        author: str = "Unknown",
        language: str = "en",
    ):
        """
        Convert markdown content to EPUB format.

        Args:
            markdown_content: Markdown content with LaTeX equations
            output_path: Path for output EPUB file
            title: Book title
            author: Author name
            language: Language code
        """
        import markdown
        from markdown.extensions import tables, fenced_code, codehilite

        output_path = Path(output_path)
        logger.info(f"Creating EPUB: {output_path.name}")

        # Create EPUB book
        book = epub.EpubBook()
        book.set_identifier(f"paper2epub_{title}")
        book.set_title(title)
        book.set_language(language)
        book.add_author(author)

        # Convert markdown to HTML
        md = markdown.Markdown(
            extensions=[
                'extra',
                'codehilite',
                'fenced_code',
                'tables',
                'nl2br',
            ]
        )
        html_content = md.convert(markdown_content)

        # Add MathJax/KaTeX support for LaTeX equations
        mathjax_script = """
        <script type="text/javascript" async
          src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/tex-mml-chtml.js">
        </script>
        """

        # Create CSS
        css_content = """
        body {
            font-family: Georgia, serif;
            line-height: 1.6;
            margin: 2em;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: Arial, sans-serif;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
        }
        pre {
            background-color: #f4f4f4;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        """

        # Add CSS
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=css_content,
        )
        book.add_item(nav_css)

        # Create chapter
        chapter = epub.EpubHtml(
            title=title,
            file_name="content.xhtml",
            lang=language,
        )
        chapter.content = f"""
        <html>
        <head>
            <link rel="stylesheet" href="style/nav.css" type="text/css"/>
            {mathjax_script}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        book.add_item(chapter)

        # Create table of contents
        book.toc = (chapter,)
        book.spine = ["nav", chapter]

        # Add navigation files
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Write EPUB file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        epub.write_epub(str(output_path), book)
        logger.info(f"EPUB created successfully: {output_path}")

    def convert(
        self,
        pdf_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        title: Optional[str] = None,
        author: str = "Unknown",
        language: str = "en",
        save_markdown: bool = False,
    ) -> Path:
        """
        Convert academic PDF to EPUB format.

        Args:
            pdf_path: Path to input PDF file
            output_path: Path for output EPUB (defaults to same name as PDF)
            title: Book title (defaults to PDF filename)
            author: Author name
            language: Language code
            save_markdown: Whether to save intermediate markdown file

        Returns:
            Path to created EPUB file
        """
        pdf_path = Path(pdf_path)

        # Set defaults
        if output_path is None:
            output_path = pdf_path.with_suffix(".epub")
        else:
            output_path = Path(output_path)

        if title is None:
            title = pdf_path.stem

        logger.info(f"Starting conversion: {pdf_path.name} -> {output_path.name}")

        # Step 1: Extract PDF to Markdown
        markdown_content = self.extract_pdf_to_markdown(pdf_path)

        # Optionally save markdown
        if save_markdown:
            markdown_path = pdf_path.with_suffix(".md")
            markdown_path.write_text(markdown_content, encoding="utf-8")
            logger.info(f"Saved markdown: {markdown_path}")

        # Step 2: Convert Markdown to EPUB
        self.markdown_to_epub(
            markdown_content=markdown_content,
            output_path=output_path,
            title=title,
            author=author,
            language=language,
        )

        logger.info(f"Conversion complete: {output_path}")
        return output_path
