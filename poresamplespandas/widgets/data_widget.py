from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QLabel, QSpacerItem, QSizePolicy, \
    QPushButton, QComboBox, QSpinBox, QFrame, QLineEdit
from PySide6.QtGui import Qt

import qtawesome as qta


# This is where the data lives
class DataWidget(QWidget):
    def __init__(self):
        super(DataWidget, self).__init__()

    
        self.vbox = QVBoxLayout()
        self.vbox.setObjectName(u"verticalLayout")
        self.splitter = QSplitter()
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)

        self.flowcell_edit = QLineEdit()
        self.vbox.addWidget(self.splitter)
        self.setLayout(self.vbox)

        self.pos_ctrl_count_spin = QSpinBox()
        self.neg_ctrl_count_spin = QSpinBox()
        self.restore_combo = QComboBox()
        self.reset_sort_button = QPushButton("reset sort")

        self.pos_ctrl_count_spin.setDisabled(True)
        self.neg_ctrl_count_spin.setDisabled(True)
        self.restore_combo.setDisabled(True)
        self.reset_sort_button.setDisabled(True)

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
        bhbox.addWidget(self.flowcell_edit)
        bhbox.addWidget(self.get_vline())
        bhbox.addSpacerItem(hspacer)
        bhbox.addWidget(self.get_vline())
        bhbox.addWidget(self.reset_sort_button)
        bhbox.addWidget(self.get_vline())
        bhbox.addWidget(QLabel("restore samples"))
        bhbox.addWidget(self.restore_combo)

        bvbox.insertLayout(0, bhbox)
       # bvbox.addWidget(self.sample_table_view)
        bottom_widget.setLayout(bvbox)

        tvbox = QVBoxLayout()
       # tvbox.addWidget(self.plate_table_view)
        top_widget.setLayout(tvbox)
        top_widget.setMaximumHeight(250)
        top_widget.setContentsMargins(0, 0, 0, 10)
        tvbox.setContentsMargins(0, 0, 0, 0)

        self.splitter.addWidget(top_widget)
        self.splitter.addWidget(bottom_widget)


    

