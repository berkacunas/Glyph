import os
import json

from PyQt6.QtCore import QSettings, QCoreApplication, QStandardPaths
from PyQt6.QtWidgets import QDialog, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QMessageBox, QFileDialog, QGroupBox, QPushButton

class SettingsDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(QCoreApplication.translate("SettingsDialog", "Settings"))
        self.setFixedSize(300, 200)

        self.settings = QSettings()

        self.setupUi()
        self.loadSettings()

    def setupUi(self):

        mainLayout = QVBoxLayout(self)

        languageGroupBox = QGroupBox(QCoreApplication.translate("SettingsDialog", "Language Settings"))
        languageHLayout = QHBoxLayout()

        self.languageLabel = QLabel(QCoreApplication.translate("SettingsDialog", "Language:"))
        self.languageComboBox = QComboBox()
        self.languageComboBox.addItem(QCoreApplication.translate("SettingsDialog", "English"), "en")
        self.languageComboBox.addItem(QCoreApplication.translate("SettingsDialog", "Turkish"), "tr")

        languageHLayout.addWidget(self.languageLabel)
        languageHLayout.addWidget(self.languageComboBox)
        languageGroupBox.setLayout(languageHLayout)
        mainLayout.addWidget(languageGroupBox)

        backupGroupBox = QGroupBox(QCoreApplication.translate("SettingsDialog", "Backup / Restore Settings"))
        backupVLayout = QVBoxLayout()

        exportHLayout = QHBoxLayout()
        self.exportButton = QPushButton(QCoreApplication.translate("SettingsDialog", "Export Settings..."))
        self.exportButton.clicked.connect(self.exportSettings)
        exportHLayout.addWidget(self.exportButton)
        backupVLayout.addLayout(exportHLayout)

        importHLayout = QHBoxLayout()
        self.importButton = QPushButton(QCoreApplication.translate("SettingsDialog", "Import Settings..."))
        self.importButton.clicked.connect(self.importSettings)
        importHLayout.addWidget(self.importButton)
        backupVLayout.addLayout(importHLayout)

        backupGroupBox.setLayout(backupVLayout)
        mainLayout.addWidget(backupGroupBox)

        # ... Daha sonra eklenecek ayarları buraya yaz ...

        mainLayout.addStretch()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        mainLayout.addWidget(self.buttonBox)

    def loadSettings(self):

        current_lang = self.settings.value("language/current", "en", type=str)
        index = self.languageComboBox.findData(current_lang)
        if index != -1:
            self.languageComboBox.setCurrentIndex(index)
        # ... Eklenecek ayarlar burada yüklenebilir..

    def saveSettings(self):

            selected_lang_code = self.languageComboBox.currentData()
            self.settings.setValue("language/current", selected_lang_code)
            # ... Eklenecek ayarlar burada kaydedilebilir ...

            self.settings.sync()
        
    def exportSettings(self):
        default_filename = f"{QCoreApplication.applicationName()}_settings.json"
        default_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        initial_path = os.path.join(default_path, default_filename)

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            QCoreApplication.translate("SettingsDialog", "Export Settings"),
            initial_path,
            QCoreApplication.translate("SettingsDialog", "JSON Files (*.json);;All Files (*)")
        )

        if file_path:
            try:
                all_settings = {}
                for key in self.settings.allKeys():
                    all_settings[key] = self.settings.value(key)

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(all_settings, f, indent=4, ensure_ascii=False)

                QMessageBox.information(
                    self,
                    QCoreApplication.translate("SettingsDialog", "Export Successful"),
                    QCoreApplication.translate("SettingsDialog", f"Settings have been successfully exported to:\n{file_path}")
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    QCoreApplication.translate("SettingsDialog", "Export Failed"),
                    QCoreApplication.translate("SettingsDialog", f"Failed to export settings.\nError: {str(e)}")
                )

    def importSettings(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            QCoreApplication.translate("SettingsDialog", "Import Settings"),
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation),
            QCoreApplication.translate("SettingsDialog", "JSON Files (*.json);;All Files (*)")
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_settings = json.load(f)

                confirm = QMessageBox.question(
                    self,
                    QCoreApplication.translate("SettingsDialog", "Confirm Import"),
                    QCoreApplication.translate("SettingsDialog", "Importing settings will overwrite your current settings. Do you want to continue?"),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )

                if confirm == QMessageBox.StandardButton.Yes:
                    self.settings.clear()
                    for key, value in imported_settings.items():
                        self.settings.setValue(key, value)
                    self.settings.sync()
                    self.loadSettings()
                    
                    QMessageBox.information(
                        self,
                        QCoreApplication.translate("SettingsDialog", "Import Successful"),
                        QCoreApplication.translate("SettingsDialog", "Settings have been successfully imported. Please restart the application for some changes (like language) to take full effect.")
                    )
                else:
                    return
                    # self.statusBar().showMessage(QCoreApplication.translate("SettingsDialog", "Import cancelled by user."), 2000) # Bu metot QDialog'da yok, hata verir. Ana pencere status bar'ı güncellenmeliydi.
                    # QDialog'un kendi status bar'ı olmadığı için bu satırı çıkarıyoruz veya ana pencereden bir sinyal gönderip güncelletiyoruz.
                    # Şimdilik bu satırı kaldırıyorum, aksi halde SettingsDialog'da statusBar hatası alırsınız.
                    # Eğer çok istenirse, parent'a bir sinyal emit edilebilir.

            except json.JSONDecodeError:
                QMessageBox.critical(
                    self,
                    QCoreApplication.translate("SettingsDialog", "Import Failed"),
                    QCoreApplication.translate("SettingsDialog", "Failed to import settings. The selected file is not a valid JSON format.")
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    QCoreApplication.translate("SettingsDialog", "Import Failed"),
                    QCoreApplication.translate("SettingsDialog", f"Failed to import settings.\nError: {str(e)}")
                )
