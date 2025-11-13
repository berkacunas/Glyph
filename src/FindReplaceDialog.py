from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QCheckBox, QVBoxLayout, QHBoxLayout, QGridLayout

class FindReplaceDialog(QDialog):

    findNextSignal = pyqtSignal(str, bool, bool)  # (text, case_sensitive, whole_words)
    replaceSignal = pyqtSignal(str, str, bool, bool)
    replaceAllSignal = pyqtSignal(str, str, bool, bool)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(self.tr("Find & Replace"))
        self.setModal(False) 

        self.lblFind = QLabel(self.tr("Find:"))
        self.txtFind = QLineEdit()
        
        self.lblReplace = QLabel(self.tr("Replace:"))
        self.txtReplace = QLineEdit()

        self.chkCase = QCheckBox(self.tr("Case sensitive"))
        self.chkWords = QCheckBox(self.tr("Whole words only"))

        self.btnFind = QPushButton(self.tr("Find Next"))
        self.btnReplace = QPushButton(self.tr("Replace"))
        self.btnReplaceAll = QPushButton(self.tr("Replace All"))
        self.btnClose = QPushButton(self.tr("Close"))

        layout = QGridLayout()
        layout.addWidget(self.lblFind, 0, 0)
        layout.addWidget(self.txtFind, 0, 1, 1, 2)
        
        layout.addWidget(self.lblReplace, 1, 0)
        layout.addWidget(self.txtReplace, 1, 1, 1, 2)

        layout.addWidget(self.chkCase, 2, 0, 1, 2)
        layout.addWidget(self.chkWords, 3, 0, 1, 2)

        btnLayout = QVBoxLayout()
        btnLayout.addWidget(self.btnFind)
        btnLayout.addWidget(self.btnReplace)
        btnLayout.addWidget(self.btnReplaceAll)
        btnLayout.addWidget(self.btnClose)
        btnLayout.addStretch()

        mainLayout = QHBoxLayout()
        mainLayout.addLayout(layout)
        mainLayout.addLayout(btnLayout)
        
        self.setLayout(mainLayout)

        self.btnFind.clicked.connect(self.on_find_next)
        self.btnReplace.clicked.connect(self.on_replace)
        self.btnReplaceAll.clicked.connect(self.on_replace_all)
        self.btnClose.clicked.connect(self.close)

    def on_find_next(self):
        text = self.txtFind.text()
        if text:
            self.findNextSignal.emit(text, self.chkCase.isChecked(), self.chkWords.isChecked())

    def on_replace(self):
        text = self.txtFind.text()
        if text:
            self.replaceSignal.emit(text, self.txtReplace.text(), self.chkCase.isChecked(), self.chkWords.isChecked())

    def on_replace_all(self):
        text = self.txtFind.text()
        if text:
            self.replaceAllSignal.emit(text, self.txtReplace.text(), self.chkCase.isChecked(), self.chkWords.isChecked())
