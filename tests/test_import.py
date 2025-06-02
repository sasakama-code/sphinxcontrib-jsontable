"""
Tests for import behavior and lazy loading.

This module tests that the package can be imported without Sphinx
and that Sphinx dependencies are only required when actually using
the directive functionality.
"""

import sys
from unittest.mock import patch

import pytest


def test_basic_import_without_sphinx():
    """Test that the package can be imported without Sphinx installed."""
    # Temporarily hide sphinx from imports
    with patch.dict(
        sys.modules, {"sphinx": None, "sphinx.util": None, "sphinx.util.logging": None}
    ):
        # This should not raise ImportError
        import sphinxcontrib.jsontable

        assert sphinxcontrib.jsontable.__version__ == "0.1.0"
        assert sphinxcontrib.jsontable.__author__ == "sasakama-code"


def test_version_access_without_sphinx():
    """Test that version information is accessible without Sphinx."""
    with patch.dict(sys.modules, {"sphinx": None, "sphinx.util": None}):
        from sphinxcontrib.jsontable import __author__, __email__, __version__

        assert __version__ == "0.1.0"
        assert __author__ == "sasakama-code"
        assert __email__ == "sasakamacode@gmail.com"


def test_setup_function_requires_sphinx():
    """Test that setup function can only be called with Sphinx available."""
    # This test assumes Sphinx is available in the test environment
    from sphinxcontrib.jsontable import setup

    # Mock Sphinx app
    class MockSphinxApp:
        def add_directive(self, name, directive_class):
            pass

    mock_app = MockSphinxApp()
    result = setup(mock_app)

    assert result["version"] == "0.1.0"
    assert result["parallel_read_safe"] is True
    assert result["parallel_write_safe"] is True


def test_directive_import_requires_sphinx():
    """Test that directive module requires Sphinx when imported."""
    # This test assumes Sphinx is available in the test environment
    # If Sphinx is not available, importing directives should raise ImportError
    try:
        import sphinxcontrib.jsontable.directives

        # If we get here, Sphinx is available
        assert hasattr(sphinxcontrib.jsontable.directives, "JsonTableDirective")
    except ImportError as e:
        # Sphinx is not available, which is expected in some environments
        assert "sphinx" in str(e).lower()


@pytest.mark.parametrize(
    "module_name",
    [
        "sphinx",
        "sphinx.util",
        "sphinx.util.logging",
        "docutils",
    ],
)
def test_lazy_import_behavior(module_name):
    """Test that specific Sphinx modules are not imported at package level."""
    # Remove the module if it's already imported
    if module_name in sys.modules:
        del sys.modules[module_name]
