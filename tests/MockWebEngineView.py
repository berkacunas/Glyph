from unittest.mock import MagicMock
from PySide6.QtWidgets import QWidget

class MockWebEngineView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def settings(self):
        # settings() çağrıldığında hata vermek yerine
        # "setAttribute" metoduna sahip boş bir MagicMock döndür.
        dummy_settings = MagicMock()
        dummy_settings.setAttribute = MagicMock()
        return dummy_settings

    def setHtml(self, html, baseUrl=None):
        pass # HTML yüklemeyi de sessizce geçiştir