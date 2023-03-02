from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QPushButton,
    QComboBox,
    QSpinBox,
    QFrame,
    QLineEdit,
    QMainWindow,
    QTableWidget,
    QTableView,
)
from PySide6.QtGui import Qt

from PySide6.QtCore import QAbstractTableModel

import qtawesome as qta


class DataWidget(QWidget):
    def __init__(
        self,
        sample_table_view: QTableView,
        table_widget: QTableWidget,
        mainwindow: QMainWindow,
        name_of_file: str = None,
    ) -> None:
        super(DataWidget, self).__init__()

        # main window:
        self.mainwindow = mainwindow

        # main layout
        self.vbox = QVBoxLayout()
        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Vertical)
        self.vbox.addWidget(self.splitter)
        self.setLayout(self.vbox)
        bottom_widget = QWidget()
        top_widget = QWidget()
        bvbox = QVBoxLayout()
        bhbox = QHBoxLayout()
        tvbox = QVBoxLayout()
        hspacer = QSpacerItem(5, 5, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # name of the file
        self.filename = QLabel(name_of_file) or QLabel("Current file")

        # refresh barcode button
        self.refresh_barcodes = QPushButton("Refresh barcodes")

        # add to layout
        bvbox.setContentsMargins(0, 0, 0, 0)
        bhbox.setContentsMargins(0, 10, 0, 5)
        # add controls
        bhbox.addWidget(QLabel("+ ctrls"))
        bhbox.addWidget(self.mainwindow.pos_spinbox)
        bhbox.addWidget(self.get_vline())
        bhbox.addWidget(QLabel("- ctrls"))
        bhbox.addWidget(self.mainwindow.neg_spinbox)
        bhbox.addWidget(self.get_vline())
        bhbox.addWidget(self.refresh_barcodes)
        bhbox.addSpacerItem(hspacer)
        bhbox.addWidget(self.get_vline())
        bhbox.addWidget(QLabel("restore samples"))
        bhbox.addWidget(self.mainwindow.removed_samples)
        bvbox.insertLayout(0, bhbox)
        bvbox.addWidget(sample_table_view)
        bottom_widget.setLayout(bvbox)
        # add the name of the file
        tvbox.addWidget(QLabel("Currently working on file:"))
        tvbox.addWidget(self.filename)
        tvbox.addWidget(table_widget)
        top_widget.setLayout(tvbox)
        # size of the plate view
        top_widget.setMaximumHeight(350)
        top_widget.setContentsMargins(0, 0, 0, 10)
        tvbox.setContentsMargins(0, 0, 0, 0)
        self.splitter.addWidget(top_widget)
        self.splitter.addWidget(bottom_widget)

    def get_vline(self):
        line = QFrame()
        line.setFixedWidth(2)
        return line
