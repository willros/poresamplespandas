from PySide6.QtWidgets import (
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QLabel,
    QFormLayout,
    QComboBox,
    QLineEdit,
    QListWidget,
    QTextEdit,
    QTextBrowser,
    QSizePolicy,
    QAbstractItemView,
    QMainWindow,
)
from PySide6.QtCore import Qt
import qtawesome as qta

from ..import_data.import_barcodes import make_barcodes_df2


class TabMenu(QTabWidget):
    def __init__(self, mainwindow: QMainWindow):
        super(TabMenu, self).__init__()

        self.main_window = mainwindow

        self.setStyleSheet(
            "QTabWidget::pane { margin: -10px -9px -13px -9px; border: none; }"
        )
        self.vs = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        # which size??
        self.setFixedWidth(200)

        # to hide the toggle bar above the tab bar
        self.tabBar().hide()
        # hide the tab bar from the start
        self.hide()

        # initialize tabs, buttons and lists
        self.tabs = {}
        self.barcode_buttons = {}
        self.barcode_lists = {}

        # create the tabs
        self.mk_file_tab()
        self.mk_barcode_tab()
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

    def mk_barcode_tab(self):
        tab = QWidget()
        tab.setContentsMargins(0, 0, 0, 0)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # change this
        barcodes = self.main_window.barcode_df
        for bc in barcodes.kit.unique():
            barcode_df = barcodes.loc[lambda x: x.kit == bc]

            self.barcode_buttons[bc] = QPushButton(bc)
            self.barcode_buttons[bc].setObjectName(bc)
            self.barcode_buttons[bc].clicked.connect(self.toggle_barcode_visibility)

            self.barcode_lists[bc] = QListWidget()
            self.barcode_lists[bc].setObjectName(bc)
            self.barcode_lists[bc].setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )
            self.barcode_lists[bc].setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.barcode_lists[bc].setDragEnabled(True)
            self.barcode_lists[bc].setStatusTip(f"Barcode set barcodes")
            self.barcode_lists[bc].hide()

            layout.addWidget(self.barcode_buttons[bc])
            layout.addWidget(self.barcode_lists[bc])

        # add layout
        tab.setLayout(layout)
        self.tabs["barcode"] = tab
        self.addTab(tab, "barcode")

        # clear the barcode_lists
        self.update_barcodes()

    def update_barcodes(self):
        barcodes = self.main_window.barcode_df
        for bc in barcodes.kit.unique():
            self.barcode_lists[bc].clear()
            barcode_df = barcodes.loc[lambda x: x.kit == bc]
            # add items
            self.barcode_lists[bc].addItems(barcode_df.name.to_list())

    def mk_file_tab(self):
        tab = QWidget()
        tab.setContentsMargins(0, 0, 0, 0)
        layout = QVBoxLayout()

        self.button_import = QPushButton("Import samples")
        self.button_import.setStatusTip("Import samples")
        self.button_import.setIcon(qta.icon("fa5s.file-import", color="white"))
        self.button_import.setStyleSheet("QPushButton { text-align: left; }")

        self.button_export = QPushButton("Export sheet")
        self.button_export.setStatusTip("Export samplesheet")
        self.button_export.setIcon(qta.icon("fa5s.file-export", color="white"))
        self.button_export.setStyleSheet("QPushButton { text-align: left; }")

        self.file_type = QComboBox()
        # change this to real values
        self.file_type.addItems(["analytix", "dummy1", "dummy2"])

        # add to layout:
        layout.addWidget(self.button_import)
        layout.addWidget(self.button_export)
        layout.addWidget(QLabel("Origin of file to import: "))
        layout.addWidget(self.file_type)
        layout.addSpacerItem(self.vs)
        tab.setLayout(layout)

        self.tabs["file"] = tab
        self.addTab(tab, "file")

    def mk_help_tab(self):
        tab = QWidget()
        tab.setContentsMargins(0, 0, 0, 0)
        layout = QVBoxLayout()

        logOutput = QTextEdit()
        logOutput.setReadOnly(True)
        logOutput.setLineWrapMode(QTextEdit.NoWrap)
        logOutput.setMarkdown(
            """
This is the help text for \n
poresamples.

Shortcuts: \n

Save file: Ctrl-S \n
Open file: Ctrl-O \n
Regret barcode: Ctrl-Z \n
        """
        )

        layout.addWidget(logOutput)
        tab.setLayout(layout)
        self.tabs["help"] = tab
        self.addTab(tab, "help")

    def toggle_barcode_visibility(self):
        name = self.sender().objectName()
        if self.barcode_lists[name].isVisible():
            self.barcode_lists[name].hide()
        else:
            self.barcode_lists[name].show()
