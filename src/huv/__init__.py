"""
huv - Hierarchical UV Virtual Environment Manager

A complete wrapper around uv that adds hierarchical virtual environment support
where child environments can inherit packages from parent environments with
proper precedence handling, while passing through all other uv commands unchanged.

Features:
- Create hierarchical virtual environments with automatic inheritance
- Smart pip install that skips packages available from parent environments
- pip uninstall with visibility into what remains available from parents
- Complete passthrough for all other uv commands (run, sync, lock, etc.)
- Drop-in replacement for uv with added hierarchy features
"""

__version__ = "0.3.0"
__author__ = "Hierarchical Virtual Environment Team"
__email__ = "hvenv@example.com"
__description__ = "Hierarchical UV Virtual Environment Manager"

from .main import HierarchicalUV, main

__all__ = ["HierarchicalUV", "main"]

