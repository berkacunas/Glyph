import pytest
import os
import sys

from unittest.mock import MagicMock

from MockWebEngineView import MockWebEngineView

mock_widgets_module = MagicMock()
mock_widgets_module.QWebEngineView = MockWebEngineView
sys.modules["PySide6.QtWebEngineWidgets"] = mock_widgets_module

mock_core_module = MagicMock()
sys.modules["PySide6.QtWebEngineCore"] = mock_core_module

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from Glyph import MarkdownEditor

def test_app_icon_is_set(qtbot):
    """
    Test if the main window has a valid icon set.
    """
    editor = MarkdownEditor()
    qtbot.addWidget(editor)

    icon = editor.windowIcon()

    assert not icon.isNull(), "Application icon is null!"

    available_sizes = icon.availableSizes()
    assert len(available_sizes) > 0, "Icon loaded but has no valid sizes (file might be missing or path wrong)"
