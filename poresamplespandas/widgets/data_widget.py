from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QLabel, QSpacerItem, QSizePolicy, \
    QPushButton, QComboBox, QSpinBox, QFrame, QLineEdit, QMainWindow, QTableWidget, QTableView
from PySide6.QtGui import Qt

from PySide6.QtCore import QAbstractTableModel

import qtawesome as qta


class DataWidget(QWidget):
    def __init__(self, 
                 sample_table_view: QTableView,
                 table_widget: QTableWidget,
                 mainwindow: QMainWindow) -> None:
        super(DataWidget, self).__init__()            
        
        # main window:
        self.mainwindow = mainwindow

        # button (belong to the main window)
        self.pos_button = self.mainwindow.pos_button
        self.neg_button = self.mainwindow.neg_button
        
        # disable buttons before data is loaded
        self.pos_button.setDisabled(False)
        self.neg_button.setDisabled(False)
        self.mainwindow.removed_samples.setDisabled(False)
            
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
        hspacer = QSpacerItem(5, 5, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # add to layout
        bvbox.setContentsMargins(0, 0, 0, 0)
        bhbox.setContentsMargins(0, 10, 0, 5)
        bhbox.addWidget(QLabel("+ ctrls"))
        bhbox.addWidget(self.neg_button)
        bhbox.addWidget(self.get_vline())
        bhbox.addWidget(QLabel("- ctrls"))
        bhbox.addWidget(self.pos_button)
        bhbox.addWidget(self.get_vline())
        bhbox.addWidget(self.get_vline())
        bhbox.addSpacerItem(hspacer)
        bhbox.addWidget(self.get_vline())
        bhbox.addWidget(self.get_vline())
        bhbox.addWidget(QLabel("restore samples"))
        bhbox.addWidget(self.mainwindow.removed_samples)
        bvbox.insertLayout(0, bhbox)
        bvbox.addWidget(sample_table_view)
        bottom_widget.setLayout(bvbox)
        tvbox = QVBoxLayout()
        tvbox.addWidget(table_widget)
        top_widget.setLayout(tvbox)
        top_widget.setMaximumHeight(250)
        top_widget.setContentsMargins(0, 0, 0, 10)
        tvbox.setContentsMargins(0, 0, 0, 0)
        self.splitter.addWidget(top_widget)
        self.splitter.addWidget(bottom_widget)
        
    def get_vline(self):
        line = QFrame()
        line.setFixedWidth(2)
        return line


    

