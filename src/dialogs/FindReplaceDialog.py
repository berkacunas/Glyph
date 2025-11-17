from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QCheckBox, QVBoxLayout, QHBoxLayout, QGridLayout

class FindReplaceDialog(QDialog):

    findNextSignal = Signal(str, bool, bool)  # (text, case_sensitive, whole_words)
    replaceSignal = Signal(str, str, bool, bool)
    replaceAllSignal = Signal(str, str, bool, bool)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(self.tr("Find & Replace"))
        self.setModal(False) 

        self.labelFind = QLabel(self.tr("Find:"))
        self.textFind = QLineEdit()
        
        self.labelReplace = QLabel(self.tr("Replace:"))
        self.textReplace = QLineEdit()

        self.checkCase = QCheckBox(self.tr("Case sensitive"))
        self.checkWords = QCheckBox(self.tr("Whole words only"))

        self.buttonFind = QPushButton(self.tr("Find Next"))
        self.buttonReplace = QPushButton(self.tr("Replace"))
        self.buttonReplaceAll = QPushButton(self.tr("Replace All"))
        self.buttonClose = QPushButton(self.tr("Close"))

        layout = QGridLayout()
        layout.addWidget(self.labelFind, 0, 0)
        layout.addWidget(self.textFind, 0, 1, 1, 2)
        
        layout.addWidget(self.labelReplace, 1, 0)
        layout.addWidget(self.textReplace, 1, 1, 1, 2)

        layout.addWidget(self.checkCase, 2, 0, 1, 2)
        layout.addWidget(self.checkWords, 3, 0, 1, 2)

        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(self.buttonFind)
        buttonLayout.addWidget(self.buttonReplace)
        buttonLayout.addWidget(self.buttonReplaceAll)
        buttonLayout.addWidget(self.buttonClose)
        buttonLayout.addStretch()

        mainLayout = QHBoxLayout()
        mainLayout.addLayout(layout)
        mainLayout.addLayout(buttonLayout)
        
        self.setLayout(mainLayout)

        self.buttonFind.clicked.connect(self.on_find_next)
        self.buttonReplace.clicked.connect(self.on_replace)
        self.buttonReplaceAll.clicked.connect(self.on_replace_all)
        self.buttonClose.clicked.connect(self.close)

    def on_find_next(self):
        text = self.textFind.text()
        if text:
            self.findNextSignal.emit(text, self.checkCase.isChecked(), self.checkWords.isChecked())

    def on_replace(self):
        text = self.textFind.text()
        if text:
            self.replaceSignal.emit(text, self.textReplace.text(), self.checkCase.isChecked(), self.checkWords.isChecked())

    def on_replace_all(self):
        text = self.textFind.text()
        if text:
            self.replaceAllSignal.emit(text, self.textReplace.text(), self.checkCase.isChecked(), self.checkWords.isChecked())
