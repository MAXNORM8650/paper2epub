# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
