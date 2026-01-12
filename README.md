# paper2epub

A powerful academic PDF to EPUB converter with AI-powered layout detection and LaTeX math support.

## Features

- **Academic-First Design**: Optimized for scientific papers, research documents, and technical publications
- **LaTeX Math Support**: Preserves mathematical equations using Nougat's neural OCR
- **Complex Layout Handling**: AI-powered detection of multi-column layouts, tables, and figures
- **GPU Acceleration**: Optional CUDA/MPS (Apple Silicon) support for faster processing
- **Figure Extraction**: Automatic extraction and embedding of figures using PyMuPDF
- **Multiple Output Formats**: EPUB3 with optional intermediate Markdown
- **Easy to Use**: Both CLI and Python API available

## Installation

### Basic Installation

```bash
pip install paper2epub
```

### From Source

```bash
git clone https://github.com/MAXNORM8650/paper2epub.git
cd paper2epub
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Requirements

- Python 3.9+
- PyTorch 2.0+
- For GPU acceleration:
  - NVIDIA GPU: CUDA-enabled PyTorch
  - Apple Silicon (M1/M2/M3): MPS-enabled PyTorch (included by default)

## Quick Start

### Command Line

```bash
# Basic conversion
paper2epub paper.pdf

# Specify output and metadata
paper2epub paper.pdf -o output.epub -t "My Paper" -a "John Doe"

# Use larger model with GPU
paper2epub paper.pdf -m base -d cuda

# Save intermediate markdown
paper2epub paper.pdf --save-markdown

# Skip figure extraction
paper2epub paper.pdf --no-figures

# Set minimum figure size (filter small images)
paper2epub paper.pdf --figure-min-size 150
```

### Python API

```python
from paper2epub import Paper2EpubConverter

# Initialize converter
converter = Paper2EpubConverter(
    model_tag="0.1.0-small",  # or "0.1.0-base" for better quality
    device="auto",             # auto-detect GPU/CPU
    extract_figures=True,      # enable figure extraction
    figure_min_size=100,       # minimum figure size in pixels
)

# Convert PDF to EPUB
output_path = converter.convert(
    pdf_path="paper.pdf",
    title="My Academic Paper",
    author="John Doe",
    save_markdown=True,        # optionally save .md file
)

print(f"Created: {output_path}")
```

## CLI Options

```
Usage: paper2epub [OPTIONS] PDF_PATH

Options:
  -o, --output PATH          Output EPUB file path
  -t, --title TEXT           Book title
  -a, --author TEXT          Author name
  -l, --language TEXT        Language code (default: en)
  -m, --model [small|base]   Nougat model size (default: small)
  -d, --device [auto|cuda|mps|cpu]  Device to use
  -b, --batch-size INT       Batch size for processing
  --save-markdown            Save intermediate markdown file
  --no-figures               Skip figure extraction from PDF
  --figure-min-size INT      Minimum figure size in pixels (default: 100)
  -v, --verbose              Enable verbose logging
  --version                  Show version
  --help                     Show this message and exit
```

## How It Works

paper2epub uses a multi-stage pipeline:

1. **PDF Extraction**: Nougat (Meta's neural OCR) extracts text, tables, and LaTeX equations
2. **Figure Extraction**: PyMuPDF extracts embedded images from the PDF
3. **Markdown Generation**: Content is converted to Markdown with preserved structure
4. **EPUB Creation**: Markdown and images are transformed into EPUB3 with MathML/MathJax support

### Why Nougat?

[Nougat](https://github.com/facebookresearch/nougat) (Neural Optical Understanding for Academic Documents) is Meta's state-of-the-art model specifically designed for academic papers. It excels at:

- Recognizing complex mathematical notation
- Handling multi-column layouts
- Preserving table structures
- Extracting figures and captions

## Model Sizes

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| small | ~350MB | Fast | Good | Quick conversions, testing |
| base | ~1.2GB | Moderate | Better | Production use, complex papers |

## Performance

- **CPU**: 1-3 pages/minute (small model)
- **GPU (CUDA)**: 10-20 pages/minute
- **Apple Silicon (MPS)**: 5-15 pages/minute

## Examples

### Convert Multiple PDFs

```bash
for pdf in *.pdf; do
    paper2epub "$pdf" -a "Author Name"
done
```

### Batch Processing in Python

```python
from pathlib import Path
from paper2epub import Paper2EpubConverter

converter = Paper2EpubConverter()

pdf_dir = Path("papers")
for pdf_file in pdf_dir.glob("*.pdf"):
    print(f"Converting {pdf_file.name}...")
    converter.convert(pdf_file)
```

## Limitations

- Scanned PDFs may require higher quality OCR (use base model)
- Very complex equations might need manual review
- Image quality depends on source PDF resolution
- EPUB readers vary in math rendering support (MathJax recommended)

## Troubleshooting

### Dependency Conflicts

**Issue 1: albumentations**

If you get an error about `albumentations` or `ImageCompression`:

```bash
# Install compatible version
pip install 'albumentations<1.4.0'
```

**Issue 2: pypdfium2 (PdfDocument has no attribute 'render')**

If you get an error about `'PdfDocument' object has no attribute 'render'`:

```bash
# Install compatible version
pip install 'pypdfium2>=4.0.0,<5.0.0'
```

**Or reinstall with all fixes:**

```bash
pip install --upgrade paper2epub
```

### Out of Memory

```bash
# Reduce batch size
paper2epub paper.pdf -b 1

# Use CPU instead of GPU
paper2epub paper.pdf -d cpu
```

### Poor Quality Output

```bash
# Use larger model
paper2epub paper.pdf -m base

# Enable verbose logging to debug
paper2epub paper.pdf -v
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [Nougat](https://github.com/facebookresearch/nougat) by Meta AI Research
- [ebooklib](https://github.com/aerkalov/ebooklib) for EPUB creation
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF handling

## Citation

If you use paper2epub in academic work, please cite:

```bibtex
@software{paper2epub,
  title = {paper2epub: Academic PDF to EPUB Converter},
  author = {Komal Kumar},
  year = {2026},
  url = {https://github.com/MAXNORM8650/paper2epub}
}
```

For Nougat:
```bibtex
@article{blecher2023nougat,
  title={Nougat: Neural Optical Understanding for Academic Documents},
  author={Blecher, Lukas and Cucurull, Guillem and Scialom, Thomas and Stojnic, Robert},
  journal={arXiv preprint arXiv:2308.13418},
  year={2023}
}
```

## Support

- Issues: [GitHub Issues](https://github.com/MAXNORM8650/paper2epub/issues)
- Discussions: [GitHub Discussions](https://github.com/MAXNORM8650/paper2epub/discussions)

## Roadmap

- [ ] GROBID integration for better metadata extraction
- [ ] Support for more input formats (DOCX, LaTeX)
- [ ] Batch processing UI
- [ ] Cloud/API deployment option
- [ ] Enhanced equation rendering options
- [ ] Custom styling templates
