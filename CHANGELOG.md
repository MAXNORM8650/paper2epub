# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-01-12

### Added
- **Figure Extraction**: Automatic extraction and embedding of figures using PyMuPDF
  - `FigureExtractor` class for extracting images from PDFs
  - `FigureMatcher` class for matching figure references in text
  - Configurable minimum figure size filtering
- New CLI options:
  - `--no-figures`: Skip figure extraction from PDF
  - `--figure-min-size`: Set minimum figure size in pixels (default: 100)
- Lazy model loading for faster initialization
- Custom exception hierarchy (`Paper2EpubError`, `PDFExtractionError`, `FigureExtractionError`, `EPUBCreationError`, `ModelLoadError`)
- Memory cleanup method for better resource management
- Comprehensive test suite with mocked fixtures for CI
- GitHub Actions workflows:
  - `tests.yml`: Multi-platform test matrix (Ubuntu, macOS, Windows) with Python 3.8-3.12
  - `lint.yml`: Code formatting and linting checks
  - `publish.yml`: PyPI publishing with trusted publishing
- PEP 561 type hints support (`py.typed` marker)

### Changed
- Version bump to 0.2.0 (Beta status)
- Updated project URLs to MAXNORM8650 GitHub repository
- Enhanced converter to support image embedding in EPUB output

### Fixed
- Images now properly embedded in EPUB output
- Memory management improvements

## [0.1.0] - 2026-01-12

### Added
- Initial release
- Nougat-based PDF to EPUB conversion
- Support for academic papers with LaTeX math
- CLI interface with multiple options
- Python API for programmatic use
- GPU acceleration support (CUDA, MPS/Apple Silicon)
- Automatic device detection
- Intermediate markdown output option
- Batch processing examples
- Comprehensive documentation
- Basic test suite

### Features
- Complex layout detection
- Table extraction and formatting
- Mathematical equation preservation
- Multi-language support
- EPUB3 with MathML/MathJax support

### Fixed
- Dependency compatibility with albumentations (<1.4.0)
- Dependency compatibility with pypdfium2 (4.x series)
- LazyDataset API usage for Nougat 0.1.17+
- PDF rasterization with correct pypdfium2 version
