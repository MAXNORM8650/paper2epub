#!/bin/bash

# Setup script for paper2epub dependencies
# This script installs all required dependencies with correct versions

set -e

echo "=========================================="
echo "paper2epub Dependency Setup"
echo "=========================================="
echo

# Fix critical dependency versions
echo "Installing compatibility fixes..."
pip install 'albumentations<1.4.0' 'pypdfium2>=4.0.0,<5.0.0'

echo
echo "✓ Dependencies installed successfully!"
echo

# Verify installation
echo "Verifying installation..."
python -c "
from paper2epub import Paper2EpubConverter
import pypdfium2

print('✓ paper2epub import successful')
print('✓ pypdfium2 v4.x installed')

# Check if PdfDocument has render method
if hasattr(pypdfium2.PdfDocument, 'render'):
    print('✓ PdfDocument.render() available')
else:
    print('✗ Warning: PdfDocument.render() not found')
    exit(1)

from nougat.dataset.rasterize import rasterize_paper
print('✓ rasterize_paper import successful')

print()
print('All checks passed! Run:')
print('  paper2epub your_paper.pdf')
"

echo
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
