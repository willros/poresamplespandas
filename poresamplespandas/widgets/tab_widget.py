from PySide6.QtWidgets import (QTabWidget, QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QLabel, QFormLayout, QComboBox, QLineEdit, QListWidget, QTextEdit, QTextBrowser)
from PySide6.QtGui import QAction
import qtawesome as qta



class TabMenu(QTabWidget):
    def __init__(self, barcodes: QListWidget):
        super(TabMenu, self).__init__()

        self.setStyleSheet("QTabWidget::pane { margin: -10px -9px -13px -9px; border: none; }")
        self.vs = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)
        
        # which size??
        self.setFixedWidth(200)
        
        #to hide the toggle bar above the tab bar
        self.tabBar().hide()
        #hide the tab bar from the start 
        self.hide()
        
        # create the tabs
        self.tabs = {}
        self.mk_file_tab()
        self.mk_barcode_tab(barcodes)
        self.mk_help_tab()


    def open_tab(self, input_):
        if self.currentWidget() == self.tabs[input_]:
            self.toggle_visibility()
        else: 
            self.setCurrentWidget(self.tabs[input_])
            self.show()
            
    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            
    def mk_barcode_tab(self, barcodes: QListWidget):
        tab = QWidget()
        tab.setContentsMargins(0, 0, 0, 0)
        layout = QVBoxLayout()
        layout.addWidget(barcodes)
        tab.setLayout(layout)
        self.tabs['barcode'] = tab
        self.addTab(tab, "barcode")

    def mk_file_tab(self):
        tab = QWidget()
        tab.setContentsMargins(0,0,0,0)
        layout = QVBoxLayout()

        self.button_import = QPushButton("Import samples")
        self.button_import.setStatusTip("Import samples")
        self.button_import.setIcon(qta.icon("fa5s.file-import", color='white'))
        self.button_import.setStyleSheet("QPushButton { text-align: left; }")

        self.button_export = QPushButton("Export sheet")
        self.button_export.setStatusTip("Export samplesheet")
        self.button_export.setIcon(qta.icon("fa5s.file-export", color='white'))
        self.button_export.setStyleSheet("QPushButton { text-align: left; }")
        
        self.file_type = QComboBox()
        self.file_type.addItems(['analytix', 'illumina', 'nanopore'])

        # add to layout:
        layout.addWidget(self.button_import)
        layout.addWidget(self.button_export)
        layout.addWidget(QLabel("Origin of file to import: "))
        layout.addWidget(self.file_type)
        layout.addSpacerItem(self.vs)
        tab.setLayout(layout)
        
        self.tabs['file'] = tab
        self.addTab(tab, "file")

    def mk_help_tab(self):
        tab = QWidget()
        tab.setContentsMargins(0, 0, 0, 0)
        layout = QVBoxLayout()
        
        logOutput = QTextEdit()
        logOutput.setReadOnly(True)
        logOutput.setLineWrapMode(QTextEdit.NoWrap)
        logOutput.setMarkdown("""
This is the help text for \n
poresamples.

Shortcuts: \n

Save file: Ctrl-S \n
Open file: Ctrl-O \n
Regret barcode: Ctrl-Z \n
        """)
        

        layout.addWidget(logOutput)
        tab.setLayout(layout)
        self.tabs['help'] = tab
        self.addTab(tab, "help")

        

