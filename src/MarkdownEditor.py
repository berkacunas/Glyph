import os
import glob

from PyQt6.QtCore import Qt, QDir, QUrl, QModelIndex, QPoint
from PyQt6.QtGui import QAction, QIcon, QFileSystemModel
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, \
                            QSplitter, QMessageBox, QFileDialog, QTreeView, QDialog, QTabWidget, QMenu

from PyQt6.QtWebEngineWidgets import QWebEngineView 
import markdown

from .SettingsDialog import SettingsDialog

ICONS_DIR = os.path.join(os.path.dirname(__file__), "assets", "icons")

markdown_extensions = [
    'fenced_code',  # code blocks. ex. ```python ... ```
    'codehilite',   # adds syntax highlighting (requires pygments package)
    'admonition',   # !!! note block
    'tables',       # tables
    'toc',          # table of contents. use it with [TOC] placeholder
    'def_list',     # syntax for definition lists
    'attr_list',    # attribute lists to generated HTML
    'sane_lists',   # enables list items with multiple paragraphs
    'footnotes'
]

class MarkdownEditor(QMainWindow):

    def __init__(self):

        super().__init__()

        self.markdown = markdown.Markdown(extensions=markdown_extensions)
        self.editor_content_changed = False
        self.current_file_path = None
        self.is_model_set = False

        self.setMinimumSize(1200, 800)
        self.setWindowTitle(self.tr("Glyph"))
        
        self.mainWidget = QWidget()

        self.mainVLayout = QVBoxLayout(self.mainWidget)
        # self.editorGroupBox = QGroupBox(title=self.tr("Markdowns"))
        self.editorWidget = QWidget()
        self.editorVLayout = QVBoxLayout()

        self.editorHSplitter = QSplitter()
        self.editorHSplitter.setOrientation(Qt.Orientation.Horizontal)

        self.editorVLayout.addWidget(self.editorHSplitter)
        self.editorWidget.setLayout(self.editorVLayout)

        # self.mainVLayout.addLayout(self.menuHLayout ,stretch=0)
        self.mainVLayout.addWidget(self.editorWidget, stretch=1)
        self.setCentralWidget(self.mainWidget)

        self.setupUi()
        self.createIcons()
        self.createActions()
        self.createMenuBar()
        self.createToolBar()
        self.createContextMenu()
        self.statusBar().showMessage(self.tr("Ready"))

    def setupUi(self):

        self.fileSysModel = QFileSystemModel()
        # self.fileSysModel.setRootPath(QDir.currentPath())
        self.fileSysModel.setNameFilters(["*.md"])
        self.fileSysModel.setNameFilterDisables(False)

        self.fileSysTreeView = QTreeView()
        self.fileSysTreeView.setHeaderHidden(True) # Başlıkları göster
        self.fileSysTreeView.setAnimated(True) # Animasyonlu genişletme/daraltma
        self.fileSysTreeView.setIndentation(20) # Girinti mesafesi
        self.fileSysTreeView.setSortingEnabled(False) # Sıralama aktif (sütun başlıklarına tıklayınca)
        self.fileSysTreeView.clicked.connect(self.on_filesystree_item_clicked)

        # self.md_editor = self._createEditor()
        self.md_viewer = QWebEngineView()

        self.editorTabWidget = QTabWidget()
        self.editorTabWidget.currentChanged.connect(self.on_editorTab_changed)
        self.editorTabWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.editorTabWidget.customContextMenuRequested.connect(self.show_editorTab_context_menu)
        self.editorTabWidget.setProperty("is_empty", True)
        self.editorTabWidget.setStyleSheet("""
            QTabWidget::pane[is_empty="true"] {
                background-color: #F0F0F0;
                border-top: 1px solid #C0C0C0;
            }
        """)
        
        self.editorHSplitter.addWidget(self.fileSysTreeView)
        self.editorHSplitter.addWidget(self.editorTabWidget)
        self.editorHSplitter.addWidget(self.md_viewer)

        # self.editorHSplitter.setChildrenCollapsible(False)
        self.editorHSplitter.setCollapsible(1, False)
        self.editorHSplitter.setCollapsible(2, True)

        self.editorHSplitter.setStretchFactor(0, 0)
        self.editorHSplitter.setStretchFactor(1, 1)
        self.editorHSplitter.setStretchFactor(2, 0)

        # self.fileSysTreeView.setMinimumWidth(200)
        # self.md_editor.setMinimumWidth(200)
        # self.md_viewer.setMinimumWidth(300)
      
    def createIcons(self):

        self.newFileIcon = QIcon(os.path.join(ICONS_DIR, "new.ico"))
        self.openFileIcon = QIcon(os.path.join(ICONS_DIR, "open.ico"))
        self.saveFileIcon = QIcon(os.path.join(ICONS_DIR, "save.ico"))
        self.saveAsFileIcon = QIcon(os.path.join(ICONS_DIR, "saveas.ico"))
        self.closeFileIcon = QIcon(os.path.join(ICONS_DIR, "close.ico"))
        self.exitAppIcon = QIcon(os.path.join(ICONS_DIR, "exit.ico"))
        
        self.cutIcon = QIcon(os.path.join(ICONS_DIR, "cut.ico"))
        self.copyIcon = QIcon(os.path.join(ICONS_DIR, "copy.ico"))
        self.pasteIcon = QIcon(os.path.join(ICONS_DIR, "paste.ico"))
        self.undoIcon = QIcon(os.path.join(ICONS_DIR, "undo.ico"))
        self.redoIcon = QIcon(os.path.join(ICONS_DIR, "redo.ico"))

        self.settingsIcon = QIcon(os.path.join(ICONS_DIR, "settings.ico"))

        self.englandFlagIcon = QIcon(os.path.join(ICONS_DIR, "england-flag.ico"))
        self.turkeyFlagIcon = QIcon(os.path.join(ICONS_DIR, "turkey-flag.ico"))

    def createActions(self):

        newFileAction = QAction(self.newFileIcon, self.tr("&New File..."), self)
        newFileAction.setShortcut("Ctrl+N")
        newFileAction.setStatusTip(self.tr("Create a new file"))
        newFileAction.triggered.connect(self.new_file) 
        self.newFileAction = newFileAction

        openFileAction = QAction(self.openFileIcon, self.tr("&Open File..."), self)
        openFileAction.setShortcut("Ctrl+O")
        openFileAction.setStatusTip(self.tr("Open file"))
        openFileAction.triggered.connect(self.open_file) 
        self.openFileAction = openFileAction

        openDirectoryAction = QAction(self.tr("Open Directory..."))
        openDirectoryAction.setStatusTip(self.tr("Open all markdown files in a directory"))
        openDirectoryAction.triggered.connect(self.open_directory) 
        self.openDirectoryAction = openDirectoryAction

        saveFileAction = QAction(self.saveFileIcon, self.tr("&Save"), self)
        saveFileAction.setShortcut("Ctrl+S")
        saveFileAction.setStatusTip(self.tr("Save file"))
        saveFileAction.triggered.connect(self.save_file) 
        self.saveFileAction = saveFileAction

        saveAsFileAction = QAction(self.saveAsFileIcon, self.tr("Save &As"), self)
        saveAsFileAction.setShortcut("Ctrl+Alt+S")
        saveAsFileAction.setStatusTip(self.tr("Save file as..."))
        saveAsFileAction.triggered.connect(self.saveas_file) 
        self.saveAsFileAction = saveAsFileAction

        closeFileAction = QAction(self.closeFileIcon, self.tr("Close"), self)
        # closeFileAction.setShortcut("Ctrl+W")
        closeFileAction.setStatusTip(self.tr("Close file"))
        closeFileAction.triggered.connect(self.close_file) 
        self.closeFileAction = closeFileAction

        exitAppAction = QAction(self.exitAppIcon, self.tr("E&xit"), self)
        exitAppAction.setShortcut("Ctrl+W")
        exitAppAction.setStatusTip(self.tr("Exit Application"))
        exitAppAction.triggered.connect(self.exit_app) 
        self.exitAppAction = exitAppAction

        cutAction = QAction(self.cutIcon, self.tr("Cu&t"), self) 
        cutAction.setShortcut("Ctrl+X")
        cutAction.setStatusTip(self.tr("Cut selected text to clipboard"))
        cutAction.triggered.connect(self.cut_text) 
        self.cutAction = cutAction

        copyAction = QAction(self.copyIcon, self.tr("&Copy"), self)
        copyAction.setShortcut("Ctrl+C")
        copyAction.setStatusTip(self.tr("Copy selected text to clipboard"))
        copyAction.triggered.connect(self.copy_text)
        self.copyAction = copyAction

        pasteAction = QAction(self.pasteIcon, self.tr("&Paste"), self)
        pasteAction.setShortcut("Ctrl+V")
        pasteAction.setStatusTip(self.tr("Paste text from clipboard"))
        pasteAction.triggered.connect(self.paste_text)
        self.pasteAction = pasteAction

        undoAction = QAction(self.undoIcon, self.tr("&Undo"), self)
        undoAction.setShortcut("Ctrl+Z")
        undoAction.setStatusTip(self.tr("Undo last action"))
        undoAction.triggered.connect(self.undo_text)
        self.undoAction = undoAction

        redoAction = QAction(self.redoIcon, self.tr("&Redo"), self)
        redoAction.setShortcut("Ctrl+Y")
        redoAction.setStatusTip(self.tr("Redo last action"))
        redoAction.triggered.connect(self.redo_text)
        self.redoAction = redoAction

        enLangAction = QAction(self.englandFlagIcon, self.tr("English"), self)
        enLangAction.triggered.connect(lambda: self.change_language('en'))
        self.enLangAction = enLangAction

        trLangAction = QAction(self.turkeyFlagIcon, self.tr("Türkçe"), self)
        trLangAction.triggered.connect(lambda: self.change_language('tr'))
        self.trLangAction = trLangAction

        settingsAction = QAction(self.settingsIcon, self.tr("&Settings..."), self)
        settingsAction.setShortcut("Ctrl+,")
        settingsAction.setStatusTip(self.tr("Open application settings"))
        settingsAction.triggered.connect(self.openSettingsDialog)
        self.settingsAction = settingsAction

    def createMenuBar(self):

        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu(self.tr("File"))
        fileMenu.addAction(self.newFileAction)
        fileMenu.addAction(self.openFileAction)
        fileMenu.addAction(self.openDirectoryAction)
        fileMenu.addAction(self.saveFileAction)
        fileMenu.addAction(self.saveAsFileAction)
        fileMenu.addAction(self.closeFileAction)
        fileMenu.addAction(self.exitAppAction)

        editMenu = menuBar.addMenu(self.tr("Edit"))
        editMenu.addAction(self.cutAction)
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        
        toolsMenu = menuBar.addMenu(self.tr("Tools"))
        toolsMenu.addAction(self.settingsAction)

        languageMenu = menuBar.addMenu(self.tr("Language"))
        selectLanguageMenu = languageMenu.addMenu(self.tr("Select"))
        selectLanguageMenu.addAction(self.enLangAction)
        selectLanguageMenu.addAction(self.trLangAction)

    def createToolBar(self):

        fileToolbar = self.addToolBar(self.tr("File")) 

        fileToolbar.addAction(self.newFileAction)
        fileToolbar.addAction(self.openFileAction)
        fileToolbar.addAction(self.openDirectoryAction)
        fileToolbar.addAction(self.saveFileAction)
        fileToolbar.addAction(self.saveAsFileAction)
        fileToolbar.addAction(self.closeFileAction)

        fileToolbar.addSeparator()

        editToolbar = self.addToolBar(self.tr("Edit")) 

        editToolbar.addAction(self.cutAction)
        editToolbar.addAction(self.copyAction)
        editToolbar.addAction(self.pasteAction)
        editToolbar.addSeparator()
        editToolbar.addAction(self.undoAction)
        editToolbar.addAction(self.redoAction)

        toolsToolbar = self.addToolBar(self.tr("Tools")) 
        toolsToolbar.addAction(self.settingsAction)

    def createContextMenu(self):

        self.tebWidgetContextMenu = QMenu(self)
        self.tebWidgetContextMenu.addAction(self.closeFileAction)
        self.tebWidgetContextMenu.addAction(QAction("test 2", self))
        self.tebWidgetContextMenu.addAction(QAction("test 3", self))

    def on_editor_content_changed(self):
        """
        Fires ONLY when the user actually types in the editor.
        Sets the 'is_changed' flag and updates the viewer.
        """
        md_editor = self._activeTextEdit()
        if not md_editor:
            return

        if not md_editor.property("is_changed"):
            md_editor.setProperty("is_changed", True)
            
            current_index = self.editorTabWidget.currentIndex()
            tab_title = self.editorTabWidget.tabText(current_index)
            if not tab_title.endswith('*'):
                self.editorTabWidget.setTabText(current_index, tab_title + '*')
        
            self.statusBar().showMessage(self.tr("Unsaved changes..."), 2000)

        self.update_viewer()

    def openSettingsDialog(self):

        dialog = SettingsDialog(self) # Diyalogu ana pencereye parent olarak atıyoruz
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog.saveSettings() # Ayarları kaydet
            QMessageBox.information(
                self,
                self.tr("Settings Saved"), # Mesaj kutusu başlığı
                self.tr("Settings have been saved. Please restart the application for some changes (like language) to take full effect.")
            )
            # Dil değişikliğini hemen uygulamak için ana pencereyi yeniden oluşturabiliriz (karmaşık)
            # veya uygulamayı yeniden başlatmayı önerebiliriz.
            # Şimdilik kullanıcıya yeniden başlatmasını söylemek en kolay yol.
        else:
            self.statusBar().showMessage(self.tr("Settings cancelled."), 2000)

    def file_selector_file_open(self, selected_file_path: str):

        with open(selected_file_path, mode="r", encoding="utf-8") as f:
            text = f.read()

        self.md_editor.setText(text)

    def new_file(self):

        activeEditor = self._activeTextEdit()
        if activeEditor and activeEditor.property("is_changed"):
            response = QMessageBox.warning(self,
                self.tr(u"Unsaved Changes"),
                self.tr(u"There are unsaved changes in the current file. Do you want to save them before creating a new file?"),
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )

            if response == QMessageBox.StandardButton.Save:
                if not self.save_file():
                    return

            elif response == QMessageBox.StandardButton.Cancel:
                return

        self._createEditor()
        self.md_viewer.setHtml("")
        
        self.setWindowTitle(self.tr("Glyph - Untitled"))
        self.statusBar().showMessage(self.tr("New file created. Ready to edit."), 3000)

    def open_file(self):

        active_editor = self._activeTextEdit()
        if active_editor and active_editor.property("is_changed"):
            response = QMessageBox.warning(self,
                self.tr("Unsaved Changes"),
                self.tr("There are unsaved changes in the current file. Do you want to save them before creating a new file?"), 
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            if response == QMessageBox.StandardButton.Save:
                if not self.save_file():
                    return
            elif response == QMessageBox.StandardButton.Cancel:
                return

        filePath, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Open Markdown File"),
            ".",
            self.tr("Markdown Files (*.md);;All Files (*)")
        )

        if filePath:
            self._open_file_in_new_tab(filePath)
        else:
            self.statusBar().showMessage(self.tr("File open cancelled."), 2000)

    def open_directory(self):
        
        directory_path = QFileDialog.getExistingDirectory(None, self.tr("Select folder:"), QDir.currentPath())

        if directory_path:
            if not self.is_model_set:
                self.fileSysTreeView.setModel(self.fileSysModel)
                self.fileSysTreeView.hideColumn(1) # Boyut
                self.fileSysTreeView.hideColumn(2) # Tip
                self.fileSysTreeView.hideColumn(3) # Değişiklik Tarihi
                self.is_model_set = True

            self.fileSysModel.setRootPath(directory_path)
            new_root_index = self.fileSysModel.index(directory_path)
            self.fileSysTreeView.setRootIndex(new_root_index)
            
            md_file_count = 0
            try:
                search_pattern = os.path.join(directory_path, '*.md')
                md_files_list = glob.glob(search_pattern)
                md_file_count = len(md_files_list)
            except Exception as e:
                # Bir hata olursa (örn: erişim izni yok)
                print(f"Dosyalar sayılırken hata: {e}")
                # Hata durumunda sayıyı 0 olarak bırak

            # 2. Mesajı oluştur
            dir_name = os.path.basename(directory_path)
            message = self.tr(f"Directory opened: {dir_name}  |  Found {md_file_count} markdown files")

            # 3. Mesajı 3 saniyeliğine (3000ms) göster
            self.statusBar().showMessage(message, 3000)

    def save_file(self) -> bool:
        
        md_editor = self._activeTextEdit()
        if not md_editor:
            return False
        
        is_changed = md_editor.property("is_changed")
        file_path = md_editor.property("file_path")

        if not is_changed:
            self.statusBar().showMessage(self.tr("No changes to save."), 2000)
            return True
        
        if not file_path:
            return self.saveas_file()


        # 3. Dosya değişmiş ve mevcut bir yolu varsa, doğrudan kaydet
        try:
            self._write_file(file_path, md_editor.toPlainText())

            md_editor.setProperty("is_changed", False) # Değişiklik bayrağını sıfırla
            
            # Sekme başlığındaki '*' işaretini kaldır
            current_index = self.editorTabWidget.currentIndex()
            tab_title = self.editorTabWidget.tabText(current_index).rstrip('*')
            self.editorTabWidget.setTabText(current_index, tab_title)
            
            self.setWindowTitle(self.tr("Glyph") + f" - {os.path.basename(file_path)}")
            self.statusBar().showMessage(self.tr(f"File saved: {os.path.basename(file_path)}"), 3000)
            return True

        except Exception as e:
            QMessageBox.critical(self, self.tr("Error Saving File"),
                self.tr(f"Could not save file '{self.current_file_path}'.\nError: {str(e)}")
            )
            self.statusBar().showMessage(self.tr("Failed to save file."), 3000)
            return False

    def saveas_file(self):
        
        md_editor = self._activeTextEdit()
        if not md_editor:
            return False # Kaydedilecek aktif bir editör yok
        
        file_path = md_editor.property("file_path")


        initial_path = file_path if file_path else os.path.expanduser("~")
        initial_filename = "Untitled.md"
        if not file_path and md_editor.toPlainText().strip():
            initial_filename = md_editor.toPlainText().strip()[:20].replace('\n', '_') + ".md"
            initial_path = os.path.join(initial_path, initial_filename)

        filePath, _ = QFileDialog.getSaveFileName(
            self, 
            self.tr("Save as File"), 
            initial_filename,
            self.tr("Markdown Files (*.md);;All Files (*)")) 
        
        if filePath:
            try:
                self._write_file(filePath, md_editor.toPlainText())

                md_editor.setProperty("file_path", filePath) 
                md_editor.setProperty("is_changed", False)

                current_index = self.editorTabWidget.currentIndex()
                self.editorTabWidget.setTabText(current_index, os.path.basename(filePath))

                self.setWindowTitle(self.tr("Glyph") + f" - {os.path.basename(filePath)}") # Pencere başlığı
                self.statusBar().showMessage(self.tr(f"File saved in: {os.path.basename(filePath)}"), 3000)
                return True

            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.tr("Error Saving File"),
                    self.tr(f"Could not save file '{filePath}'.\nError: {str(e)}")
                )
                self.statusBar().showMessage(self.tr("Failed to save file."), 3000)
                return False
        else:
            self.statusBar().showMessage(self.tr("File save cancelled."), 2000)

    def close_file(self):
        
        md_editor = self._activeTextEdit()
        if not md_editor:
            return
        
        if md_editor.property("is_changed"):
            response = QMessageBox.warning(self,
                self.tr("Unsaved Changes"),
                self.tr("There are unsaved changes in the current file. Do you want to save them before creating a new file?"), 
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            if response == QMessageBox.StandardButton.Save:
                if not self.save_file():
                    return
            elif response == QMessageBox.StandardButton.Cancel:
                return

        current_index = self.editorTabWidget.currentIndex()
        self.editorTabWidget.removeTab(current_index)
        self.md_viewer.setHtml("")

        file_path = md_editor.property("file_path")
        if file_path:
            self.statusBar().showMessage(self.tr(f"File closed: {os.path.basename(file_path)}"), 3000)
        else:
            self.statusBar().showMessage(self.tr("File closed."), 3000)

        self.setWindowTitle(self.tr("Glyph"))

    def exit_app(self):
        
        if self.editor_content_changed:
            response = QMessageBox.warning(self,
                self.tr("Unsaved Changes"),
                self.tr("There are unsaved changes in the current file. Do you want to save them before creating a new file?"), 
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            if response == QMessageBox.StandardButton.Save:
                if not self.save_file():
                    return
            elif response == QMessageBox.StandardButton.Cancel:
                return
            
        QApplication.instance().quit()

    def cut_text(self):

        md_editor = self._activeTextEdit()
        if md_editor:
            md_editor.cut()

    def copy_text(self):
        
        md_editor = self._activeTextEdit()
        if md_editor:
            md_editor.copy()

    def paste_text(self):
        
        md_editor = self._activeTextEdit()
        if md_editor:
            md_editor.paste()

    def undo_text(self):
        
        md_editor = self._activeTextEdit()
        if md_editor:
            md_editor.undo()

    def redo_text(self):
        
        md_editor = self._activeTextEdit()
        if md_editor:
            md_editor.redo()

    def closeEvent(self, event):
        if self.editor_content_changed:
            response = QMessageBox.warning(self, self.tr("Unsaved Changes"),
                self.tr("There are unsaved changes. Do you want to save them before exiting?"),
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            if response == QMessageBox.StandardButton.Save:
                if self.save_file():
                    event.accept()
                else:
                    event.ignore()

                event.accept()
            elif response == QMessageBox.StandardButton.Cancel:
                event.ignore()
            else: # Discard selected.
                event.accept()
        else:
            event.accept()

    def change_language(self, lang_code: str):

       raise NotImplementedError("change_language() is not implemented yet!") 
    """
        QMessageBox.information(
            self,
            self.tr("Language Change"),
            self.tr("Language changed. Please restart the application to apply changes fully.")
        )
        # Dil ayarını kaydet (örneğin config dosyanıza)
        # Daha sonra uygulama başlatıldığında bu ayarı okuyup doğru çevirmeni yükleyin.
        
        # Geçici olarak, direkt çevirmeni yükleyip UI'yi yeniden oluşturalım (daha kompleks bir yöntem)
        # Aslında çoğu zaman uygulama yeniden başlatılır.
        self.translator.load(f"editor_{lang_code}", os.path.join(os.path.dirname(__file__), "translations"))
        QApplication.instance().installTranslator(self.translator)
        
        # UI'yi yeniden oluşturmak (zorlu bir yöntem, uygulama yeniden başlatmak daha kolay)
        self._retranslate_ui() # UI elemanlarını yeniden çevir
    
    def _retranslate_ui(self):
        # Tüm UI metinlerini tekrar ayarlar. Bu, genellikle uygulama yeniden başlatıldığında otomatik olur.
        # Çalışma zamanı dil değiştirmeyi desteklemek için her widget'ın set text metodunu tekrar çağırmanız gerekir.
        # Basitlik adına sadece ana pencere başlığını güncelliyorum.
        self.setWindowTitle(self.tr("Advanced Markdown Editor")) # Başlık çevirisi
        # self.statusBar().showMessage(self.tr("Ready")) # Status bar mesajı da tekrar set edilmeli
        
        # Diğer tüm menü ve aksiyon metinleri de burada tekrar ayarlanmalıdır.
        # Bu, QAction'ların metinlerini yeniden ayarlamak, QMenu başlıklarını güncellemek demektir.
        # Bu yüzden, çoğu uygulama dil değişikliğinde "lütfen uygulamayı yeniden başlatın" der.
        # Kompleks bir yöntemdir, bu yüzden restart tavsiye edilir.
    """
    
    def on_filesystree_item_clicked(self, index: QModelIndex):

        if self.fileSysModel.isDir(index):
            return

        file_path = self.fileSysModel.filePath(index)
        if not file_path.endswith('.md'):
            return

        self._open_file_in_new_tab(file_path)
    
    def show_editorTab_context_menu(self, pos: QPoint):
        """
        :param pos: Sağ tıklamanın QTabWidget'a göre lokal koordinatlarını 
                    (x, y) içeren QPoint nesnesi.
        """
        
        # 'pos' parametresi, menüyü nerede göstereceğinizi bilmenizi sağlar.
        # Genellikle bu lokal 'pos'u global ekran koordinatlarına çeviririz:
        
        widget = self.sender() 
        global_pos = widget.mapToGlobal(pos)
        
        if self.editorTabWidget.count() > 0:
            self.tebWidgetContextMenu.exec(global_pos)
    
    def on_editorTab_changed(self, index: int):

        if index == -1:
            self.md_viewer.setHtml("")
            self.setWindowTitle(self.tr("Glyph"))
            self._set_editor_actions_enabled(False)
            self.editorTabWidget.setProperty("is_empty", True)
        else:
            self.update_viewer()
            md_editor = self._activeTextEdit()
            file_path = md_editor.property("file_path")
            
            if file_path:
                self.setWindowTitle(self.tr("Glyph") + f" - {os.path.basename(file_path)}")
            else:
                self.setWindowTitle(self.tr("Glyph"))
            
            self._set_editor_actions_enabled(True)
            self.editorTabWidget.setProperty("is_empty", False)

        self.editorTabWidget.style().unpolish(self.editorTabWidget)
        self.editorTabWidget.style().polish(self.editorTabWidget)

    def _open_file(self, file_path: str) -> str:

        text = None
        try:
            with open(file_path, mode="r", encoding="utf-8") as f:
                text = f.read()

            return text
        except Exception as e:
            print(f"Error in _open_file: Could not open to {file_path}. Error: {e}")
            raise

    def _write_file(self, file_path: str, content: str) -> bool:

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error in _write_file: Could not write to {file_path}. Error: {e}")
            raise

    def _createEditor(self, file_name: str = "Untitled.md", file_path: str = None) -> QTextEdit:
        """
        Creates a new QTextEdit, sets its properties, and adds it to the tab widget.
        """
        md_editor = QTextEdit()
        md_editor.textChanged.connect(self.on_editor_content_changed)
        
        md_editor.setProperty("file_path", file_path)
        md_editor.setProperty("is_changed", False)

        new_tab_index = self.editorTabWidget.addTab(md_editor, file_name)
        self.editorTabWidget.setCurrentIndex(new_tab_index)
        
        return md_editor

    def update_viewer(self):
        
        md_editor = self._activeTextEdit()
        if not md_editor:
            self.md_viewer.setHtml("")
            return

        markdown_text = md_editor.toPlainText()
        html_content = css_style + self.markdown.convert(markdown_text)

        current_file_path = md_editor.property("file_path")
        
        if current_file_path:
            base_url = QUrl.fromLocalFile(os.path.dirname(current_file_path))
        else:
            base_url = QUrl.fromLocalFile(QDir.currentPath())
            
        self.md_viewer.setHtml(html_content, baseUrl=base_url)

    def _activeTextEdit(self) -> QTextEdit:
        """
        Returns the currently active QTextEdit widget in the tab widget.
        """
        activeWidget = self.editorTabWidget.currentWidget()
        
        if isinstance(activeWidget, QTextEdit):
            return activeWidget
            
        return None

    def _open_file_in_new_tab(self, file_path: str):
        """
        Bir dosyayı yeni bir sekmede açar.
        Eğer dosya zaten açıksa, o sekmeye odaklanır.
        """
        
        # 1. Dosya zaten açık mı diye kontrol et
        for i in range(self.editorTabWidget.count()):
            editor = self.editorTabWidget.widget(i)
            if isinstance(editor, QTextEdit) and editor.property("file_path") == file_path:
                self.editorTabWidget.setCurrentIndex(i)
                self.statusBar().showMessage(self.tr(f"File already open: {os.path.basename(file_path)}"), 2000)
                return

        # 2. Dosya açık değilse, oku
        try:
            text = self._open_file(file_path) # Bu sizin diski okuyan fonksiyonunuz
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Error Opening File"),
                self.tr(f"Could not open file '{os.path.basename(file_path)}'.\nError: {str(e)}")
            )
            return

        # 3. Yeni bir editör (sekme) oluştur ve içeriği ata
        file_name = os.path.basename(file_path)
        md_editor = self._createEditor(file_name=file_name, file_path=file_path)
        
        md_editor.setPlainText(text) # setPlainText, 'setText'ten daha güvenlidir
        
        # textChanged sinyali 'setPlainText' ile tetiklendi, 
        # bu yüzden 'is_changed' bayrağını manuel olarak sıfırlamalıyız.
        md_editor.setProperty("is_changed", False)
        current_index = self.editorTabWidget.currentIndex()
        self.editorTabWidget.setTabText(current_index, file_name) # '*' işaretini kaldır

        self.setWindowTitle(self.tr("Glyph") + f" - {file_name}")
        self.statusBar().showMessage(self.tr(f"Opened file: {file_name}"), 3000)

    def _set_editor_actions_enabled(self, enabled: bool):
        
        self.cutAction.setEnabled(enabled)
        self.copyAction.setEnabled(enabled)
        self.pasteAction.setEnabled(enabled)
        self.undoAction.setEnabled(enabled)
        self.redoAction.setEnabled(enabled)

css_style = """

<style> body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; line-height: 1.6; padding: 25px; }

/* === Kod ve Tablo Stilleri (Öncekiler) === */
code { 
    background-color: #f6f8fa; 
    padding: 3px 5px; 
    border-radius: 5px; 
    font-family: monospace;
}
pre { 
    background-color: #f6f8fa; 
    padding: 15px; 
    border-radius: 5px; 
    overflow-x: auto; 
}
table { 
    border-collapse: collapse; 
    margin: 15px 0;
}
th, td { 
    border: 1px solid #dfe2e5; 
    padding: 8px 12px; 
}
th { 
    background-color: #f6f8fa; 
}

/* === TOC (İçindekiler) Stili === */
.toc {
    background-color: #f9f9f9;
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    padding: 10px 20px;
    margin-bottom: 20px;
}
.toc ul {
    list-style-type: none;
    padding-left: 10px;
}

/* === Admonition (Not Kutuları) Stilleri === */
.admonition {
    padding: 15px;
    margin: 15px 0;
    border-left: 5px solid #ccc;
    border-radius: 4px;
    background-color: #f7f7f7;
}
.admonition-title {
    font-weight: bold;
    margin-bottom: 5px;
}
.admonition.note { border-color: #428bca; }
.admonition.warning { border-color: #f0ad4e; }
.admonition.danger { border-color: #d9534f; }

/* === YENİ: Footnotes (Dipnot) Stilleri === */
.footnote {
    border-top: 1px solid #e0e0e0;
    padding-top: 10px;
    margin-top: 20px;
    font-size: 0.9em;
}
/* Metin içindeki dipnot referans linki (1, 2, vb.) */
sup a {
    color: #0366d6;
    text-decoration: none;
}

/* === PYGMENTS KOD RENKLENDİRME STİLLERİ === */
/* Bu bloğu <style> etiketinizin içine ekleyin */

.codehilite .hll { background-color: #ffffcc }
.codehilite { background: #f8f8f8; border: 0px solid #ccc; padding: 6px 10px; border-radius: 0px; }
.codehilite .c { color: #408080; font-style: italic } /* Comment */
.codehilite .err { border: 1px solid #FF0000 } /* Error */
.codehilite .k { color: #008000; font-weight: bold } /* Keyword */
.codehilite .o { color: #666666 } /* Operator */
.codehilite .ch { color: #408080; font-style: italic } /* Comment.Hashbang */
.codehilite .cm { color: #408080; font-style: italic } /* Comment.Multiline */
.codehilite .cp { color: #BC7A00 } /* Comment.Preproc */
.codehilite .cpf { color: #408080; font-style: italic } /* Comment.PreprocFile */
.codehilite .c1 { color: #408080; font-style: italic } /* Comment.Single */
.codehilite .cs { color: #408080; font-style: italic } /* Comment.Special */
.codehilite .gd { color: #A00000 } /* Generic.Deleted */
.codehilite .ge { font-style: italic } /* Generic.Emph */
.codehilite .gr { color: #FF0000 } /* Generic.Error */
.codehilite .gh { color: #000080; font-weight: bold } /* Generic.Heading */
.codehilite .gi { color: #00A000 } /* Generic.Inserted */
.codehilite .go { color: #888888 } /* Generic.Output */
.codehilite .gp { color: #000080; font-weight: bold } /* Generic.Prompt */
.codehilite .gs { font-weight: bold } /* Generic.Strong */
.codehilite .gu { color: #800080; font-weight: bold } /* Generic.Subheading */
.codehilite .gt { color: #0044DD } /* Generic.Traceback */
.codehilite .kc { color: #008000; font-weight: bold } /* Keyword.Constant */
.codehilite .kd { color: #008000; font-weight: bold } /* Keyword.Declaration */
.codehilite .kn { color: #008000; font-weight: bold } /* Keyword.Namespace */
.codehilite .kp { color: #008000 } /* Keyword.Pseudo */
.codehilite .kr { color: #008000; font-weight: bold } /* Keyword.Reserved */
.codehilite .kt { color: #B00040 } /* Keyword.Type */
.codehilite .m { color: #666666 } /* Literal.Number */
.codehilite .s { color: #BA2121 } /* Literal.String */
.codehilite .na { color: #7D9029 } /* Name.Attribute */
.codehilite .nb { color: #008000 } /* Name.Builtin */
.codehilite .nc { color: #0000FF; font-weight: bold } /* Name.Class */
.codehilite .no { color: #880000 } /* Name.Constant */
.codehilite .nd { color: #AA22FF } /* Name.Decorator */
.codehilite .ni { color: #999999; font-weight: bold } /* Name.Entity */
.codehilite .ne { color: #D2413A; font-weight: bold } /* Name.Exception */
.codehilite .nf { color: #0000FF } /* Name.Function */
.codehilite .nl { color: #A0A000 } /* Name.Label */
.codehilite .nn { color: #0000FF; font-weight: bold } /* Name.Namespace */
.codehilite .nt { color: #008000; font-weight: bold } /* Name.Tag */
.codehilite .nv { color: #19177C } /* Name.Variable */
.codehilite .ow { color: #AA22FF; font-weight: bold } /* Operator.Word */
.codehilite .w { color: #bbbbbb } /* Text.Whitespace */
.codehilite .mb { color: #666666 } /* Literal.Number.Bin */
.codehilite .mf { color: #666666 } /* Literal.Number.Float */
.codehilite .mh { color: #666666 } /* Literal.Number.Hex */
.codehilite .mi { color: #666666 } /* Literal.Number.Integer */
.codehilite .mo { color: #666666 } /* Literal.Number.Oct */
.codehilite .sa { color: #BA2121 } /* Literal.String.Affix */
.codehilite .sb { color: #BA2121 } /* Literal.String.Backtick */
.codehilite .sc { color: #BA2121 } /* Literal.String.Char */
.codehilite .dl { color: #BA2121 } /* Literal.String.Delimiter */
.codehilite .sd { color: #BA2121; font-style: italic } /* Literal.String.Doc */
.codehilite .s2 { color: #BA2121 } /* Literal.String.Double */
.codehilite .se { color: #BB6622; font-weight: bold } /* Literal.String.Escape */
.codehilite .sh { color: #BA2121 } /* Literal.String.Heredoc */
.codehilite .si { color: #BB6688; font-weight: bold } /* Literal.String.Interpol */
.codehilite .sx { color: #008000 } /* Literal.String.Other */
.codehilite .sr { color: #BB6688 } /* Literal.String.Regex */
.codehilite .s1 { color: #BA2121 } /* Literal.String.Single */
.codehilite .ss { color: #19177C } /* Literal.String.Symbol */
.codehilite .bp { color: #008000 } /* Name.Builtin.Pseudo */
.codehilite .fm { color: #0000FF } /* Name.Function.Magic */
.codehilite .vc { color: #19177C } /* Name.Variable.Class */
.codehilite .vg { color: #19177C } /* Name.Variable.Global */
.codehilite .vi { color: #19177C } /* Name.Variable.Instance */
.codehilite .vm { color: #19177C } /* Name.Variable.Magic */
.codehilite .il { color: #666666 } /* Literal.Number.Integer.Long */

</style>
"""