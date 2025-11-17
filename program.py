import os
import sys
from PySide6.QtCore import Qt, QCoreApplication, QTranslator, QLocale, QSettings
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QFont

from src.Glyph import MarkdownEditor

if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./assets/icons/markdown.ico"))

    QCoreApplication.setOrganizationName("Deponessoft") # Kendi şirket adınızı veya geliştirici adınızı yazın
    QCoreApplication.setApplicationName("Glyph")

    settings = QSettings()
    last_lang = settings.value("language/current", QLocale().system().name().split('_')[0], type=str) # Varsayılan olarak sistem dili veya "en"

    translator = QTranslator()
    
    if translator.load(f"editor_{last_lang}", os.path.join(os.path.dirname(__file__), "translations")):
        app.installTranslator(translator)
    else:
        print(f"Warning: Could not load translator for {last_lang}. Defaulting to source language.")
        
    mainWindow = MarkdownEditor()
    mainWindow.show()
    sys.exit(app.exec())

