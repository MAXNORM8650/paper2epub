"""
paper2epub: A powerful academic PDF to EPUB converter
"""

__version__ = "0.2.0"
__author__ = "Komal Kumar"
__email__ = "suryavansi8650@gmail.com"

from paper2epub.converter import Paper2EpubConverter
from paper2epub.figure_extractor import FigureExtractor, FigureMatcher

__all__ = ["Paper2EpubConverter", "FigureExtractor", "FigureMatcher"]
