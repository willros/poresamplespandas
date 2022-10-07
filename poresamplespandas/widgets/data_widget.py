from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QLabel, QSpacerItem, QSizePolicy, \
    QPushButton, QComboBox, QSpinBox, QFrame, QLineEdit, QMainWindow, QTableWidget, QTableView
from PySide6.QtGui import Qt

from PySide6.QtCore import QAbstractTableModel

import qtawesome as qta


# This is where the data lives
class DataWidget(QWidget):
    def __init__(self, 
                 sample_table_view: QTableView,
                 table_widget: QTableWidget,
                 mainwindow: QMainWindow) -> None:
        super(DataWidget, self).__init__()            
        self.vbox = QVBoxLayout()
        self.vbox.setObjectName(u"verticalLayout")
        self.splitter = QSplitter()
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        
        # main window:
        self.mainwindow = mainwindow

        self.vbox.addWidget(self.splitter)
        self.setLayout(self.vbox)
        
        self.pos_ctrl_count_spin = QSpinBox()
        self.neg_ctrl_count_spin = QSpinBox()
        
        # disable buttons before data is loaded
        self.pos_ctrl_count_spin.setDisabled(True)
        self.neg_ctrl_count_spin.setDisabled(True)
        self.mainwindow.removed_samples.setDisabled(True)

        bottom_widget = QWidget()
        top_widget = QWidget()

        hspacer = QSpacerItem(5, 5, QSizePolicy.Expanding, QSizePolicy.Minimum)

        bvbox = QVBoxLayout()
        bhbox = QHBoxLayout()

        bvbox.setContentsMargins(0, 0, 0, 0)
        bhbox.setContentsMargins(0, 10, 0, 5)
        bhbox.addWidget(QLabel("+ ctrls"))
        bhbox.addWidget(self.neg_ctrl_count_spin)
        bhbox.addWidget(self.get_vline())
        bhbox.addWidget(QLabel("- ctrls"))
        bhbox.addWidget(self.pos_ctrl_count_spin)
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


    

