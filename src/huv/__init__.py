"""
huv - Hierarchical UV Virtual Environment Manager

A wrapper around uv to create hierarchical virtual environments where child environments
can inherit packages from parent environments with proper precedence handling.

Features:
- Create hierarchical virtual environments with automatic inheritance
- Smart pip install that skips packages available from parent environments
- pip uninstall with visibility into what remains available from parents
- Full compatibility with uv and standard virtual environments
"""

__version__ = "0.1.0"
__author__ = "Hierarchical Virtual Environment Team"
__email__ = "hvenv@example.com"
__description__ = "Hierarchical UV Virtual Environment Manager"

from .main import HierarchicalUV, main

__all__ = ["HierarchicalUV", "main"]