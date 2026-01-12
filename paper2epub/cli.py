"""
Command-line interface for paper2epub
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import click

from paper2epub import Paper2EpubConverter, __version__


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


@click.command()
@click.argument("pdf_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    help="Output EPUB file path (default: same as PDF name)",
)
@click.option(
    "-t",
    "--title",
    type=str,
    help="Book title (default: PDF filename)",
)
@click.option(
    "-a",
    "--author",
    type=str,
    default="Unknown",
    help="Author name",
)
@click.option(
    "-l",
    "--language",
    type=str,
    default="en",
    help="Language code (default: en)",
)
@click.option(
    "-m",
    "--model",
    type=click.Choice(["small", "base"]),
    default="small",
    help="Nougat model size (default: small)",
)
@click.option(
    "-d",
    "--device",
    type=click.Choice(["auto", "cuda", "mps", "cpu"]),
    default="auto",
    help="Device to use (default: auto-detect)",
)
@click.option(
    "-b",
    "--batch-size",
    type=int,
    default=1,
    help="Batch size for processing (default: 1)",
)
@click.option(
    "--save-markdown",
    is_flag=True,
    help="Save intermediate markdown file",
)
@click.option(
    "--no-figures",
    is_flag=True,
    help="Skip figure extraction from PDF",
)
@click.option(
    "--figure-min-size",
    type=int,
    default=100,
    help="Minimum figure size in pixels (default: 100)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose logging",
)
@click.version_option(version=__version__)
def main(
    pdf_path: Path,
    output: Optional[Path],
    title: Optional[str],
    author: str,
    language: str,
    model: str,
    device: str,
    batch_size: int,
    save_markdown: bool,
    no_figures: bool,
    figure_min_size: int,
    verbose: bool,
):
    """
    Convert academic PDF to EPUB format with LaTeX math support.

    PDF_PATH: Path to the input PDF file

    Examples:

    \b
    # Basic conversion
    $ paper2epub paper.pdf

    \b
    # Specify output and metadata
    $ paper2epub paper.pdf -o output.epub -t "My Paper" -a "John Doe"

    \b
    # Use larger model with GPU
    $ paper2epub paper.pdf -m base -d cuda

    \b
    # Save intermediate markdown
    $ paper2epub paper.pdf --save-markdown
    """
    setup_logging(verbose)

    logger = logging.getLogger(__name__)

    try:
        click.echo(f"paper2epub v{__version__}")
        click.echo(f"Converting: {pdf_path.name}")
        click.echo()

        # Map model size to model tag
        model_tag = f"0.1.0-{model}"

        # Handle auto device
        device_arg = None if device == "auto" else device

        # Initialize converter
        converter = Paper2EpubConverter(
            model_tag=model_tag,
            device=device_arg,
            batch_size=batch_size,
            extract_figures=not no_figures,
            figure_min_size=figure_min_size,
        )

        # Convert
        output_path = converter.convert(
            pdf_path=pdf_path,
            output_path=output,
            title=title,
            author=author,
            language=language,
            save_markdown=save_markdown,
        )

        click.echo()
        click.secho("✓ Conversion complete!", fg="green", bold=True)
        click.echo(f"Output: {output_path}")

        if save_markdown:
            markdown_path = pdf_path.with_suffix(".md")
            click.echo(f"Markdown: {markdown_path}")

    except FileNotFoundError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)
    except ImportError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        click.echo("\nInstall dependencies with: pip install paper2epub", err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Conversion failed")
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
