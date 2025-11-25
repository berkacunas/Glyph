import pytest
import os
import sys
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from Glyph import MarkdownEditor

def test_app_icon_is_set(qtbot):
    """
    Test if the main window has a valid icon set.
    Note: 'qtbot' is a fixture from pytest-qt (we need to install it).
    """
    editor = MarkdownEditor()
    qtbot.addWidget(editor)

    icon = editor.windowIcon()

    assert not icon.isNull(), "Application icon is null!"

    available_sizes = icon.availableSizes()
    assert len(available_sizes) > 0, "Icon loaded but has no valid sizes (file might be missing or path wrong)"
