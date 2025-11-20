import sys
import os
import glob
import urllib.parse

from PySide6.QtCore import Qt, QDir, QUrl, QModelIndex, QPoint, QSettings
from PySide6.QtGui import QAction, QIcon, QFont, QTextCursor, QTextDocument, QDesktopServices, QFontMetricsF
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QDockWidget, QTextEdit, QFileSystemModel, \
                            QSplitter, QMessageBox, QFileDialog, QTreeView, QDialog, QTabWidget, QMenu, QSizePolicy, QLabel

from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView 

import markdown
import pymdownx.emoji
import bleach

from .dialogs.FindReplaceDialog import FindReplaceDialog
from .SettingsDialog import SettingsDialog

class MarkdownEditor(QMainWindow):

    MARKDOWN_EXTENSIONS = [
        'fenced_code',      # code blocks. ex. ```python ... ```
        'codehilite',       # adds syntax highlighting (requires pygments package)
        'admonition',       # !!! note block
        'tables',           # tables
        'toc',              # table of contents. use it with [TOC] placeholder
        'def_list',         # syntax for definition lists
        'attr_list',        # attribute lists to generated HTML
        'sane_lists',       # enables list items with multiple paragraphs
        'pymdownx.emoji',   # pymdownx package
        'footnotes'
    ]

    MARKDOWN_EXTENSION_CONFIGS = {
        'pymdownx.emoji': { 
            'emoji_index': pymdownx.emoji.gemoji,
            'emoji_generator': pymdownx.emoji.to_alt,
            "alt": 'html_entity',
            "options": {
                "attributes": {
                    "align": "absmiddle",
                    "height": "20px",
                    "width": "20px"
                }
            }
        }
    }

    def __init__(self):

        super().__init__()

        self.icons_dir = self.get_resource_path(os.path.join("assets", "icons"))

        css_file_path = self.get_resource_path(os.path.join("assets", "css", "main.css"))
        self.css_file_url = QUrl.fromLocalFile(css_file_path).toString()

        qss_file_path = self.get_resource_path(os.path.join("assets", "css", "glyph_style.qss"))
        try:
            with open(qss_file_path, "r", encoding="utf-8") as f:
                qss_content = f.read()
                
            self.setStyleSheet(qss_content)
        except FileNotFoundError as fe:
            raise fe
        except Exception as e:
            raise e
        
        self.markdown = markdown.Markdown(extensions=self.MARKDOWN_EXTENSIONS, extension_configs=self.MARKDOWN_EXTENSION_CONFIGS)
        self.editor_content_changed = False
        self.current_file_path = None
        self.is_model_set = False

        self.setMinimumSize(1200, 800)
        self.setWindowTitle(self.tr("Glyph"))
        
        self.mainWidget = QWidget()

        self.mainVLayout = QVBoxLayout(self.mainWidget)
        self.editorWidget = QWidget()
        self.editorVLayout = QVBoxLayout()

        self.mainContentSplitter = QSplitter()
        self.mainContentSplitter.setOrientation(Qt.Orientation.Horizontal)

        self.editorVLayout.addWidget(self.mainContentSplitter)
        self.editorWidget.setLayout(self.editorVLayout)

        # self.mainVLayout.addLayout(self.menuHLayout ,stretch=0)
        self.mainVLayout.addWidget(self.editorWidget, stretch=1)
        self.setCentralWidget(self.mainWidget)

        self.findReplaceDialog = None
        
        # Help Menu (Singleton) Attributes
        self.readme_dialog = None
        self.readme_viewer = None

        self.setupUi()
        self.createIcons()
        self.createActions()
        self.createMenuBar()
        self.createToolBar()
        self.createContextMenu()

        self.setWindowIcon(self.appIcon)
        QApplication.instance().setWindowIcon(self.appIcon)

        if os.name == 'nt':
            import ctypes
            myappid = 'berkacunas.glyph.editor.1.0.0' # Rastgele benzersiz bir ID
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.statusBar().showMessage(self.tr("Ready"))

    def setupUi(self):

        self.fileSysModel = QFileSystemModel()
        self.fileSysModel.setNameFilters(["*.md"])
        self.fileSysModel.setNameFilterDisables(False)

        self.fileSysTreeView = QTreeView()
        self.fileSysTreeView.setHeaderHidden(True)
        self.fileSysTreeView.setAnimated(True)
        self.fileSysTreeView.setIndentation(20)
        self.fileSysTreeView.setSortingEnabled(False)
        self.fileSysTreeView.clicked.connect(self.on_filesystree_item_clicked)

        self.fileTreeDock = QDockWidget(self.tr("Explorer"), self)
        self.fileTreeDock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.fileTreeDock.setWidget(self.fileSysTreeView)
        self.fileTreeDock.visibilityChanged.connect(self.on_fileTreeDock_visibility_changed)

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.fileTreeDock)

        self.md_viewer = QWebEngineView()
        # Security settings for image display from web.
        settings = self.md_viewer.settings()
        # 1. Allow local content (file://) to access internet (https://)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        # 2. Allow local content to access other local files
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

        self.editorTabWidget = QTabWidget()
        self.editorTabWidget.currentChanged.connect(self.on_editorTab_changed)
        self.editorTabWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.editorTabWidget.customContextMenuRequested.connect(self.show_editorTab_context_menu)
        self.editorTabWidget.setProperty("is_empty", True)
        
        self.mainContentSplitter.addWidget(self.editorTabWidget)
        self.mainContentSplitter.addWidget(self.md_viewer)

        self.mainContentSplitter.setStretchFactor(0, 1)
        self.mainContentSplitter.setStretchFactor(1, 1)
        
        self.md_viewer.hide()
        
        self.statsLabel = QLabel("0 lines, 0 words, 0 characters")
        self.statsLabel.setStyleSheet("padding-right: 10px;")
        self.statusBar().addPermanentWidget(self.statsLabel)
        
   
    def createIcons(self):

        self.newFileIcon = QIcon(os.path.join(self.icons_dir, "new.ico"))
        self.openFileIcon = QIcon(os.path.join(self.icons_dir, "open.ico"))
        self.openDirectoryIcon = QIcon(os.path.join(self.icons_dir, "open-directory.ico"))
        self.saveFileIcon = QIcon(os.path.join(self.icons_dir, "save.ico"))
        self.saveAsFileIcon = QIcon(os.path.join(self.icons_dir, "saveas.ico"))
        self.saveAllFileIcon = QIcon(os.path.join(self.icons_dir, "saveall.ico"))
        self.pdfIcon = QIcon(os.path.join(self.icons_dir, "pdf.ico"))
        self.sendEmailIcon = QIcon(os.path.join(self.icons_dir, "send-email.ico"))
        self.closeFileIcon = QIcon(os.path.join(self.icons_dir, "close.ico"))
        self.exitAppIcon = QIcon(os.path.join(self.icons_dir, "exit.ico"))
        
        self.cutIcon = QIcon(os.path.join(self.icons_dir, "cut.ico"))
        self.copyIcon = QIcon(os.path.join(self.icons_dir, "copy.ico"))
        self.pasteIcon = QIcon(os.path.join(self.icons_dir, "paste.ico"))
        self.undoIcon = QIcon(os.path.join(self.icons_dir, "undo.ico"))
        self.redoIcon = QIcon(os.path.join(self.icons_dir, "redo.ico"))
        self.findIcon = QIcon(os.path.join(self.icons_dir, "find.ico"))

        self.previewIcon = QIcon(os.path.join(self.icons_dir, "eye.ico"))
        self.monkeyIcon = QIcon(os.path.join(self.icons_dir, "monkey.ico"))

        self.settingsIcon = QIcon(os.path.join(self.icons_dir, "settings.ico"))
        self.englandFlagIcon = QIcon(os.path.join(self.icons_dir, "england-flag.ico"))
        self.turkeyFlagIcon = QIcon(os.path.join(self.icons_dir, "turkey-flag.ico"))

        self.readmeIcon = QIcon(os.path.join(self.icons_dir, "readme.ico")) 
        self.aboutIcon = QIcon(os.path.join(self.icons_dir, "about.ico"))

        self.handWithPenIcon = QIcon(os.path.join(self.icons_dir, "hand-with-pen.ico"))
        self.appIcon = QIcon(os.path.join(self.icons_dir, "markdown.ico"))

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

        openDirectoryAction = QAction(self.openDirectoryIcon, self.tr("Open Directory..."), self)
        openDirectoryAction.setStatusTip(self.tr("Open all markdown files in a directory"))
        openDirectoryAction.triggered.connect(self.open_directory) 
        self.openDirectoryAction = openDirectoryAction

        saveFileAction = QAction(self.saveFileIcon, self.tr("&Save"), self)
        saveFileAction.setShortcut("Ctrl+S")
        saveFileAction.setStatusTip(self.tr("Save file"))
        saveFileAction.triggered.connect(self.trigger_save_active_file) 
        self.saveFileAction = saveFileAction

        saveAsFileAction = QAction(self.saveAsFileIcon, self.tr("Save &As"), self)
        saveAsFileAction.setShortcut("Ctrl+Alt+S")
        saveAsFileAction.setStatusTip(self.tr("Save file as..."))
        saveAsFileAction.triggered.connect(self.trigger_saveas_active_file) 
        self.saveAsFileAction = saveAsFileAction

        saveAllFileAction = QAction(self.saveAllFileIcon, self.tr("Save All"), self)
        saveAllFileAction.setStatusTip(self.tr("Save all files"))
        saveAllFileAction.triggered.connect(self.saveall_file)
        self.saveAllFileAction = saveAllFileAction

        exportPdfAction = QAction(self.pdfIcon, self.tr("Export to PDF..."), self)
        exportPdfAction.setStatusTip(self.tr("Export content to PDF file"))
        exportPdfAction.triggered.connect(self.export_to_pdf)
        self.exportPdfAction = exportPdfAction

        exportAsAction = QAction(self.tr("Export As..."), self)
        exportAsAction.setStatusTip(self.tr("Export to various formats like HTML, TXT"))
        exportAsAction.triggered.connect(self.export_as)
        self.exportAsAction = exportAsAction

        sendEmailAction = QAction(self.sendEmailIcon, self.tr("Send..."), self)
        sendEmailAction.setStatusTip(self.tr("Send content as email"))
        sendEmailAction.triggered.connect(self.send_by_email)
        self.sendEmailAction = sendEmailAction

        closeFileAction = QAction(self.closeFileIcon, self.tr("Close"), self)
        closeFileAction.setShortcut("Ctrl+W")
        closeFileAction.setStatusTip(self.tr("Close file"))
        closeFileAction.triggered.connect(self.close_file) 
        self.closeFileAction = closeFileAction

        closeOtherTabsAction = QAction(self.tr("Close Others"), self)
        closeOtherTabsAction.triggered.connect(self.close_other_tabs)
        self.closeOtherTabsAction = closeOtherTabsAction

        closeAllTabsAction = QAction(self.tr("Close All"), self)
        closeAllTabsAction.triggered.connect(self.close_all_tabs)
        self.closeAllTabsAction = closeAllTabsAction

        exitAppAction = QAction(self.exitAppIcon, self.tr("E&xit Glyph"), self)
        exitAppAction.setShortcut("Ctrl+Q")
        exitAppAction.setStatusTip(self.tr("Exit Glyph"))
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

        findReplaceAction = QAction(self.findIcon, self.tr("Find && Replace..."), self)
        findReplaceAction.setShortcut("Ctrl+F")
        findReplaceAction.triggered.connect(self.show_find_replace_dialog)
        self.findReplaceAction = findReplaceAction

        togglePreviewAction = QAction(self.previewIcon, self.tr("Toggle Preview"), self)
        togglePreviewAction.setShortcut("Ctrl+Shift+V")
        togglePreviewAction.setStatusTip(self.tr("Show/Hide the Markdown preview pane"))
        togglePreviewAction.setCheckable(True)
        togglePreviewAction.setChecked(False)
        togglePreviewAction.toggled.connect(self.toggle_preview_panel)
        self.togglePreviewAction = togglePreviewAction

        self.toggleExplorerAction = QAction(self.monkeyIcon, self.tr("Toggle Explorer"), self)
        self.toggleExplorerAction.setStatusTip(self.tr("Show/Hide the Explorer pane"))
        self.toggleExplorerAction.setCheckable(True)
        self.toggleExplorerAction.setChecked(True) 
        self.toggleExplorerAction.toggled.connect(self.fileTreeDock.setVisible)

        enLangAction = QAction(self.englandFlagIcon, self.tr("English"), self)
        enLangAction.triggered.connect(lambda: self.change_language('en'))
        self.enLangAction = enLangAction

        trLangAction = QAction(self.turkeyFlagIcon, self.tr("Türkçe"), self)
        trLangAction.triggered.connect(lambda: self.change_language('tr'))
        self.trLangAction = trLangAction

        settingsAction = QAction(self.settingsIcon, self.tr("&Settings..."), self)
        settingsAction.setShortcut("Ctrl+,")
        settingsAction.setStatusTip(self.tr("Open application settings"))
        settingsAction.triggered.connect(self.open_settings_dialog)
        self.settingsAction = settingsAction

        showReadmeAction = QAction(self.readmeIcon, self.tr("View README"), self)
        showReadmeAction.setStatusTip(self.tr("Show the application's README file"))
        showReadmeAction.triggered.connect(self.show_readme_dialog)
        self.showReadmeAction = showReadmeAction

        showAboutAction = QAction(self.aboutIcon, self.tr("About Glyph..."), self)
        showAboutAction.setStatusTip(self.tr("Show application information"))
        showAboutAction.triggered.connect(self.show_about_dialog)
        self.showAboutAction = showAboutAction

    def createMenuBar(self):

        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu(self.tr("File"))
        fileMenu.addAction(self.newFileAction)
        fileMenu.addAction(self.openFileAction)
        fileMenu.addAction(self.openDirectoryAction)
        fileMenu.addAction(self.closeFileAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.saveFileAction)
        fileMenu.addAction(self.saveAsFileAction)
        fileMenu.addAction(self.saveAllFileAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exportPdfAction)
        fileMenu.addAction(self.exportAsAction)
        fileMenu.addAction(self.sendEmailAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAppAction)

        editMenu = menuBar.addMenu(self.tr("Edit"))
        editMenu.addAction(self.cutAction)
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addSeparator()
        editMenu.addAction(self.findReplaceAction)
        editMenu.addSeparator()
        editMenu.addAction(self.undoAction)
        editMenu.addAction(self.redoAction)

        viewMenu = menuBar.addMenu(self.tr("View"))
        viewMenu.addAction(self.toggleExplorerAction)
        viewMenu.addAction(self.togglePreviewAction)    

        toolsMenu = menuBar.addMenu(self.tr("Tools"))
        toolsMenu.addAction(self.settingsAction)

        # TEMPORARILY HIDDEN (delayed to v1.1)
        # languageMenu = menuBar.addMenu(self.tr("Language"))
        # selectLanguageMenu = languageMenu.addMenu(self.tr("Select"))
        # selectLanguageMenu.addAction(self.enLangAction)
        # selectLanguageMenu.addAction(self.trLangAction)

        helpMenu = menuBar.addMenu(self.tr("Help"))
        helpMenu.addAction(self.showReadmeAction)
        helpMenu.addAction(self.showAboutAction)

    def createToolBar(self):

        fileToolbar = self.addToolBar(self.tr("File")) 
        fileToolbar.addAction(self.newFileAction)
        fileToolbar.addAction(self.openFileAction)
        fileToolbar.addAction(self.openDirectoryAction)
        fileToolbar.addAction(self.closeFileAction)
        fileToolbar.addSeparator()
        fileToolbar.addAction(self.saveFileAction)
        fileToolbar.addAction(self.saveAsFileAction)
        fileToolbar.addAction(self.saveAllFileAction)
        fileToolbar.addSeparator()
        fileToolbar.addAction(self.exportPdfAction)
        
        editToolbar = self.addToolBar(self.tr("Edit")) 
        editToolbar.addAction(self.cutAction)
        editToolbar.addAction(self.copyAction)
        editToolbar.addAction(self.pasteAction)
        editToolbar.addSeparator()
        editToolbar.addAction(self.findReplaceAction)
        editToolbar.addSeparator()
        editToolbar.addAction(self.undoAction)
        editToolbar.addAction(self.redoAction)

        toolsToolbar = self.addToolBar(self.tr("Tools")) 
        toolsToolbar.addAction(self.settingsAction)

        previewToolbar = self.addToolBar(self.tr("Preview")) 
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        previewToolbar.addWidget(spacer)
        previewToolbar.addAction(self.togglePreviewAction)

    def createContextMenu(self):

        self.tebWidgetContextMenu = QMenu(self)
        self.tebWidgetContextMenu.addAction(self.closeFileAction)
        self.tebWidgetContextMenu.addAction(self.closeOtherTabsAction)
        self.tebWidgetContextMenu.addAction(self.closeAllTabsAction)

    def on_editor_content_changed(self):

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
        self.update_statistics()

    def open_settings_dialog(self):

        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog.saveSettings()
            self.statusBar().showMessage(self.tr("Settings saved."), 3000)

            self._apply_font_settings_to_all_tabs()
            self.update_viewer()
        else:
            self.statusBar().showMessage(self.tr("Settings cancelled."), 2000)

    def new_file(self):

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
                self.fileSysTreeView.hideColumn(1) # Size
                self.fileSysTreeView.hideColumn(2) # Type
                self.fileSysTreeView.hideColumn(3) # Modified on
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
                print(self.tr(f"Error while counting files: {e}"))

            dir_name = os.path.basename(directory_path)
            message = self.tr(f"Directory opened: {dir_name}  |  Found {md_file_count} markdown files")

            self.statusBar().showMessage(message, 3000)

    def save_file(self, md_editor: QTextEdit, tab_index: int) -> bool:

        if not md_editor:
            return False
        
        is_changed = md_editor.property("is_changed")
        file_path = md_editor.property("file_path")
        
        if not is_changed:
            return True
        
        if not file_path:
            return self.saveas_file(md_editor, tab_index)

        try:
            self._write_file(file_path, md_editor.toPlainText())
            md_editor.setProperty("is_changed", False)

            # Remove '*' from tab title.
            tab_title = self.editorTabWidget.tabText(tab_index).rstrip('*')
            self.editorTabWidget.setTabText(tab_index, tab_title)
            
            # If it is the active tab, update the main window title
            if self.editorTabWidget.currentIndex() == tab_index:
                self.setWindowTitle(self.tr("Glyph") + f" - {os.path.basename(file_path)}")

            self.statusBar().showMessage(self.tr(f"File saved: {os.path.basename(file_path)}"), 3000)
            return True

        except Exception as e:
            QMessageBox.critical(self, self.tr("Error Saving File"),
                self.tr(f"Could not save file '{self.file_path}'.\nError: {str(e)}")
            )
            self.statusBar().showMessage(self.tr("Failed to save file."), 3000)
            return False

    def saveas_file(self, md_editor: QTextEdit, tab_index: int) -> bool:
        
        if not md_editor:
            return False
        
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

                self.editorTabWidget.setTabText(tab_index, os.path.basename(filePath))
                self.statusBar().showMessage(self.tr(f"File saved as: {os.path.basename(filePath)}"), 3000)
                return True

            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.tr("Error Saving File"),
                    self.tr(f"Could not save file '{filePath}'.\nError: {str(e)}")
                )
                return False
        else:
            self.statusBar().showMessage(self.tr("File save cancelled."), 2000)
            return False
        
    def saveall_file(self):

        tab_count = self.editorTabWidget.count()
        if tab_count == 0:
            self.statusBar().showMessage(self.tr("No active document to save."), 3000)
            return

        changed_files_count = 0
        saved_files_count = 0

        for i in range(tab_count):
            editor = self.editorTabWidget.widget(i)

            if editor.property("is_changed"):
                changed_files_count += 1

                if self.save_file(editor, i):
                    saved_files_count += 1
                else:
                    self.statusBar().showMessage(self.tr("Save All operation cancelled."), 3000)
                    return
        
        if changed_files_count == 0:
            self.statusBar().showMessage(self.tr("No changes to save."), 3000)
        elif saved_files_count == changed_files_count:
            self.statusBar().showMessage(self.tr(f"All {saved_files_count} modified files saved successfully."), 3000)

    def trigger_save_active_file(self):
        
        editor = self._activeTextEdit()
        index = self.editorTabWidget.currentIndex()
        if editor:
            self.save_file(editor, index)

    def trigger_saveas_active_file(self):

        editor = self._activeTextEdit()
        index = self.editorTabWidget.currentIndex()
        if editor:
            self.saveas_file(editor, index)

    def export_to_pdf(self):

        if self.editorTabWidget.count() == 0:
            self.statusBar().showMessage(self.tr("No active document to export."), 3000)
            return
        
        current_index = self.editorTabWidget.currentIndex()
        initial_filename = self.editorTabWidget.tabText(current_index).rsplit('.', 1)[0]

        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            self.tr("Export PDF"), 
            initial_filename, 
            self.tr("PDF Files (*.pdf)")
        )

        if not file_path:
            return
        
        self.md_viewer.page().printToPdf(file_path)
        self.statusBar().showMessage(self.tr(f"Exported to PDF: {os.path.basename(file_path)}"), 3000)

    def export_as(self):

        editor = self._activeTextEdit()
        if not editor:
            self.statusBar().showMessage(self.tr("No active document to export."), 3000)
            return
        
        filters = (
            f"{self.tr('XHTML Document (*.xhtml *.html)')};;"
            f"{self.tr('Markdown Document (*.md)')};;"
            f"{self.tr('Plain Text (*.txt)')}"
        )

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, 
            self.tr("Export As"), 
            self.editorTabWidget.tabText(self.editorTabWidget.currentIndex()).rsplit('.', 1)[0], 
            filters
        )

        if not file_path:
            return
        
        content_to_write = ""

        if '(*.md)' in selected_filter:
            content_to_write = editor.toPlainText()

        elif '(*.txt)' in selected_filter:
            html_content = self.markdown.convert(editor.toPlainText())
            content_to_write = bleach.clean(html_content, strip=True, tags=[])

        elif '(*.xhtml *.html)' in selected_filter:
            md_xhtml = markdown.Markdown(
                extensions=self.MARKDOWN_EXTENSIONS,
                extension_configs=self.MARKDOWN_EXTENSION_CONFIGS,
                output_format='xhtml'
            )
            content_to_write = md_xhtml.convert(editor.toPlainText())
        
        else:
            # An unknown situation (should not exist)
            return
        
        try:
            self._write_file(file_path, content_to_write)
            self.statusBar().showMessage(self.tr(f"Successfully exported to {os.path.basename(file_path)}"), 3000)
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error Exporting File"), str(e))

    def send_by_email(self):

        editor = self._activeTextEdit()
        if not editor:
            self.statusBar().showMessage(self.tr("No active document to send."), 3000)
            return
        
        subject = self.editorTabWidget.tabText(self.editorTabWidget.currentIndex()).rstrip("*")
        body = editor.toPlainText()

        try:
            # Make characters suitable for the URL (example: make spaces %20)
            encoded_subject = urllib.parse.quote(subject)
            encoded_body = urllib.parse.quote(body)
        except Exception as e:
            self.statusBar().showMessage(self.tr(f"Error encoding text: {e}"), 3000)
            return

        mailto_url = f"mailto:?subject={encoded_subject}&body={encoded_body}"

        if not QDesktopServices.openUrl(QUrl(mailto_url)):
            self.statusBar().showMessage(self.tr("Could not open default email client."), 3000)
        else:
            self.statusBar().showMessage(self.tr("Sending content to email client..."), 3000)

    def close_file(self) -> bool:
        
        md_editor = self._activeTextEdit()
        if not md_editor:
            return True
        
        if md_editor.property("is_changed"):
            response = QMessageBox.warning(self,
                self.tr("Unsaved Changes"),
                self.tr("There are unsaved changes in the current file. Do you want to save them before creating a new file?"), 
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            if response == QMessageBox.StandardButton.Save:
                if not self.save_file():
                    return False
            elif response == QMessageBox.StandardButton.Cancel:
                return False

        current_index = self.editorTabWidget.currentIndex()
        self.editorTabWidget.removeTab(current_index)

        file_path = md_editor.property("file_path")
        if file_path:
            self.statusBar().showMessage(self.tr(f"File closed: {os.path.basename(file_path)}"), 3000)
        else:
            self.statusBar().showMessage(self.tr("File closed."), 3000)

        return True

    def close_other_tabs(self):

        try:
            keep_widget = self.editorTabWidget.widget(self._context_menu_tab_index)
            if not keep_widget:
                return
        except Exception:
            return

        while self.editorTabWidget.count() > 1:
            keep_index = self.editorTabWidget.indexOf(keep_widget)

            current_index = 0
            if current_index == keep_index:
                current_index = 1
                
            self.editorTabWidget.setCurrentIndex(current_index)
            
            if not self.close_file():
                return
            
    def close_all_tabs(self):

        while self.editorTabWidget.count() > 0:
            self.editorTabWidget.setCurrentIndex(0)
            if not self.close_file():
                return

    def exit_app(self):
        
        if self._is_any_tab_changed():
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

    def toggle_preview_panel(self, checked: bool):
        
        sizes = self.mainContentSplitter.sizes()
        editor_size = sizes[0]
        viewer_size = sizes[1]

        if checked:
            # Open the viewer
            if viewer_size > 0: 
                return # Don't touch if it's already open

            total_space = editor_size # Take the entire editor area
            new_editor_size = total_space // 2
            new_viewer_size = total_space - new_editor_size
            
            # Order new sizes with only 2 elements
            self.mainContentSplitter.setSizes([new_editor_size, new_viewer_size])
            self.md_viewer.show()
            
        else:
            # close the viewer
            if viewer_size == 0: 
                return # Don't touch if it's already close
                
            total_space = editor_size + viewer_size
            
            # Give all space to Editor
            self.mainContentSplitter.setSizes([total_space, 0])

    def show_find_replace_dialog(self):

        if self.findReplaceDialog is None:
            self.findReplaceDialog = FindReplaceDialog(self)
            self.findReplaceDialog.findNextSignal.connect(self.find_next)
            self.findReplaceDialog.replaceSignal.connect(self.replace_text)
            self.findReplaceDialog.replaceAllSignal.connect(self.replace_all)

        self.findReplaceDialog.show()
        self.findReplaceDialog.raise_()
        self.findReplaceDialog.activateWindow()

    def show_about_dialog(self):
        """
        Displays the 'About' dialog with updated info.
        """
        about_text = f"""
            <h3>{self.tr("Glyph")} v1.0</h3>
            <p>{self.tr("A modern Markdown Editor built with PySide6.")}</p>
            <p>{self.tr("Created by:")} Berk Acunaş</p>
            <p>{self.tr("License:")} GPL v3.0 (Free & Open Source)</p>
            <p>—</p>
            <p>{self.tr("This application uses the following core components:")}</p>
            <ul>
                <li>Python</li>
                <li>PySide6</li>
                <li>QWebEngine (Chromium)</li>
                <li>python-markdown</li>
                <li>Pygments</li>
            </ul>
        """
        QMessageBox.about(self, self.tr("About Glyph"), about_text)

    def show_readme_dialog(self):
        
        settings = QSettings()
        current_lang = settings.value("language/current", "en", type=str)

        readme_filename = "README.tr.md" if current_lang == "tr" else "README.md"
            
        if getattr(sys, 'frozen', False):
            target_path = readme_filename
        else:
            target_path = os.path.join("..", readme_filename)
        
        readme_path = self.get_resource_path(target_path)

        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_markdown_text = f.read()
        except FileNotFoundError:
            QMessageBox.critical(self, self.tr("Error"), self.tr("README.md file not found!"))
            return
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), f"Could not read README.md: {e}")
            return

        html_body = self.markdown.convert(readme_markdown_text)
        html_full_document = f"""
            <!DOCTYPE html><html><head>
                <meta charset="utf-8">
                <link rel="stylesheet" href="{self.css_file_url}">
            </head><body>
                {html_body}
            </body></html>
        """
        if not self.readme_dialog:
            self.readme_dialog = QDialog(self)
            self.readme_dialog.setWindowTitle(self.tr("README - Glyph"))
            self.readme_dialog.setMinimumSize(700, 800)
        
            dialog_layout = QVBoxLayout()

            # Create and save heavy QWebEngineView object once
            self.readme_viewer = QWebEngineView()
            settings = self.readme_viewer.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

            dialog_layout.addWidget(self.readme_viewer)
            self.readme_dialog.setLayout(dialog_layout)
        
        # We set 'baseUrl' to the project root directory so that relative images in the 
        # # README (if any) will work.
        root_path = self.get_resource_path("")
        base_url = QUrl.fromLocalFile(root_path)
        self.readme_viewer.setHtml(html_full_document, baseUrl=base_url)
            
        self.readme_dialog.show()
        self.readme_dialog.raise_()
        self.readme_dialog.activateWindow()
    
    def _get_find_flags(self, case_sensitive, whole_words):

        flags = QTextDocument.FindFlag(0)
        if case_sensitive:
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if whole_words:
            flags |= QTextDocument.FindFlag.FindWholeWords
        
        return flags
    
    def find_next(self, text, case_sensitive, whole_words):
        
        editor = self._activeTextEdit()
        if not editor:
            return
        
        flags = self._get_find_flags(case_sensitive, whole_words)

        found = editor.find(text, flags)
        if not found:
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            editor.setTextCursor(cursor)
            
            found = editor.find(text, flags)
            if not found:
                self.statusBar().showMessage(self.tr(f"Not found: '{text}'"), 2000)
            else:
                self.statusBar().showMessage(self.tr(f"Found '{text}' (wrapped to top)."), 2000)
        else:
            self.statusBar().showMessage(self.tr(f"Found: '{text}'"), 2000)

    def replace_text(self, find_text, replace_text, case_sensitive, whole_words):

        editor = self._activeTextEdit()
        if not editor:
            return
        
        cursor = editor.textCursor()

        if cursor.hasSelection() and cursor.selectedText() == find_text:
            cursor.insertText(replace_text)
            self.statusBar().showMessage(self.tr("Replaced."), 2000)
            self.find_next(find_text, case_sensitive, whole_words)
        else:
            self.find_next(find_text, case_sensitive, whole_words)

    def replace_all(self, find_text, replace_text, case_sensitive, whole_words):

        editor = self._activeTextEdit()
        if not editor:
            return
        
        editor.moveCursor(QTextCursor.MoveOperation.Start)

        flags = self._get_find_flags(case_sensitive, whole_words)
        count = 0

        while editor.find(find_text, flags):
            editor.textCursor().insertText(replace_text)
            count += 1

        self.statusBar().showMessage(self.tr(f"Replaced {count} occurrences."), 3000)

    def closeEvent(self, event):

        if self._is_any_tab_changed():
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
        # Save the language setting (e.g., to your config file)
        # Later, when the application starts, read this setting and load the correct translator.
        
        # Temporarily, let's load the translator directly and recreate the UI (a more complex method)
        # Usually, the application is restarted.
        self.translator.load(f"editor_{lang_code}", os.path.join(os.path.dirname(__file__), "translations"))
        QApplication.instance().installTranslator(self.translator)
        
        # Recreating the UI (a difficult method, restarting is easier)
        self._retranslate_ui() # Retranslate UI elements
    
    def _retranslate_ui(self):
        # Resets all UI texts. This usually happens automatically on application restart.
        # To support runtime language change, you need to call the set text method of every widget again.
        # For simplicity, I'm only updating the main window title.
        self.setWindowTitle(self.tr("Advanced Markdown Editor")) # Title translation
        # self.statusBar().showMessage(self.tr("Ready")) # Status bar message must also be set again
        
        # All other menu and action texts must also be set here.
        # This means resetting QAction texts, updating QMenu titles.
        # This is why most applications say "please restart the application" on language change.
        # It's a complex method, so a restart is recommended.
    """
    
    def on_filesystree_item_clicked(self, index: QModelIndex):

        if self.fileSysModel.isDir(index):
            return

        file_path = self.fileSysModel.filePath(index)
        if not file_path.endswith('.md'):
            return

        self._open_file_in_new_tab(file_path)
    
    def on_fileTreeDock_visibility_changed(self, checked: bool):

        self.toggleExplorerAction.blockSignals(True)
        self.toggleExplorerAction.setChecked(checked)
        self.toggleExplorerAction.blockSignals(False)

    def show_editorTab_context_menu(self, pos: QPoint):
        
        widget = self.sender()

        tab_index = widget.tabBar().tabAt(pos)
        if tab_index == -1:
            return
        
        self._context_menu_tab_index = tab_index

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
            
            self.update_statistics()
            
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

        md_editor = QTextEdit()
        md_editor.textChanged.connect(self.on_editor_content_changed)
        
        settings = QSettings()
        default_font = QFont("Calibri", 12)
        editor_font = settings.value("editor/font", default_font, type=QFont)
        md_editor.setFont(editor_font)

        # Set tab length to 4 spaces.
        metrics = QFontMetricsF(editor_font)
        space_width = metrics.horizontalAdvance(' ')
        md_editor.setTabStopDistance(space_width * 4)

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
        
        settings = QSettings()
        default_font = QFont("Calibri", 12)
        viewer_font = settings.value("editor/font", default_font, type=QFont)
        
        font_family = viewer_font.family()
        font_size_pt = viewer_font.pointSize()

        markdown_text = md_editor.toPlainText()
        html_body = self.markdown.convert(markdown_text)

        html_full_document = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <link rel="stylesheet" href="{self.css_file_url}">
                <style>
                body {{
                    font-family: "{font_family}";
                    font-size: {font_size_pt}pt;
                }}
            </style>
            </head>
            <body>
                {html_body}
            </body>
            </html>
        """

        current_file_path = md_editor.property("file_path")
        
        if current_file_path:
            base_url = QUrl.fromLocalFile(os.path.dirname(current_file_path))
        else:
            base_url = QUrl.fromLocalFile(QDir.currentPath())
            
        self.md_viewer.setHtml(html_full_document, baseUrl=base_url)

    def _activeTextEdit(self) -> QTextEdit:
        """
        Returns the currently active QTextEdit widget in the tab widget.
        """
        activeWidget = self.editorTabWidget.currentWidget()
        
        if isinstance(activeWidget, QTextEdit):
            return activeWidget
            
        return None

    def _open_file_in_new_tab(self, file_path: str):
        
        # 1. Check if the file is already open
        for i in range(self.editorTabWidget.count()):
            editor = self.editorTabWidget.widget(i)
            if isinstance(editor, QTextEdit) and editor.property("file_path") == file_path:
                self.editorTabWidget.setCurrentIndex(i)
                self.statusBar().showMessage(self.tr(f"File already open: {os.path.basename(file_path)}"), 2000)
                return

        # 2. If the file is not open, read it.
        try:
            text = self._open_file(file_path)
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Error Opening File"),
                self.tr(f"Could not open file '{os.path.basename(file_path)}'.\nError: {str(e)}")
            )
            return

        # 3. Create a new editor tab and assign content
        file_name = os.path.basename(file_path)
        md_editor = self._createEditor(file_name=file_name, file_path=file_path)
        
        md_editor.setPlainText(text) 
        
        # The textChanged signal was triggered by 'setPlainText',
        # so we must manually reset the 'is_changed' flag.
        md_editor.setProperty("is_changed", False)
        current_index = self.editorTabWidget.currentIndex()
        self.editorTabWidget.setTabText(current_index, file_name)

        self.setWindowTitle(self.tr("Glyph") + f" - {file_name}")
        self.statusBar().showMessage(self.tr(f"Opened file: {file_name}"), 3000)

    def _set_editor_actions_enabled(self, enabled: bool):
        
        self.cutAction.setEnabled(enabled)
        self.copyAction.setEnabled(enabled)
        self.pasteAction.setEnabled(enabled)
        self.undoAction.setEnabled(enabled)
        self.redoAction.setEnabled(enabled)

    def _is_any_tab_changed(self) -> bool:
        """Helper function to check if any tab has unsaved changes."""
        for i in range(self.editorTabWidget.count()):
            editor = self.editorTabWidget.widget(i)
            if isinstance(editor, QTextEdit) and editor.property("is_changed"):
                return True
        return False
    
    def _apply_font_settings_to_all_tabs(self):
        
        settings = QSettings()
        new_font = settings.value("editor/font", QFont("Calibri", 12), type=QFont)
        
        metrics = QFontMetricsF(new_font)
        new_tab_width = metrics.horizontalAdvance(' ') * 4

        for i in range(self.editorTabWidget.count()):
            editor = self.editorTabWidget.widget(i)
            if isinstance(editor, QTextEdit):
                editor.setFont(new_font)
                editor.setTabStopDistance(new_tab_width)

    def get_resource_path(self, relative_path):
        """
        A helper method that finds the correct file paths both in the 
        development environment and when packaged with PyInstaller.
        """
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller ile paketlenmişse geçici klasörden al
            base_path = sys._MEIPASS
        else:
            # Normal çalışıyorsa proje kök dizininden al
            # (src klasörünün bir üstü)
            base_path = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(base_path, relative_path)
    
    def update_statistics(self):
        
        md_editor = self._activeTextEdit()
        if not md_editor:
            self.statsLabel.setText("")
            return
        
        text = md_editor.toPlainText()
        char_count = len(text)
        word_count = len(text.strip().split()) if text.strip() else 0
        line_count = text.count('\n') + 1 if text else 0

        self.statsLabel.setText(self.tr(f"{line_count} lines, {word_count} words, {char_count} chars"))
        
        
        
    
    