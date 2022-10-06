import pandas as pd

from PySide6.QtWidgets import (
    QTableView,
    QApplication,
    QHeaderView,
    QTableWidgetItem,
    QTableWidget,
    QMenu,
    QComboBox,
    QLabel,
    QListWidget,
    QAbstractItemView,
    QListWidgetItem
)
from PySide6.QtCore import (
    QAbstractTableModel,
    Qt,
    QModelIndex,
    QSortFilterProxyModel,
    Slot,
    QPoint,
)
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QAction

import sys
import yaml
from pathlib import Path

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, model: QAbstractTableModel,
                 data: str, 
                 barcodes: str) -> None:
        super().__init__()

        # Main model
        self.source_model = self.create_model(model, data)

        # Source view
        self.table_source = SampleTableView(main_window=self)
        self.table_source.setModel(self.source_model)

        # Table Widget
        self.setup_table_widget()

        # Hide columns
        self._hide_columns()

        # search bar
        self.seach_bar = QtWidgets.QLineEdit()

        # buttons
        self.pos_button = QtWidgets.QPushButton("POSITIVE")
        self.pos_button.setObjectName("positiv")

        self.neg_button = QtWidgets.QPushButton("NEGATIVE")
        self.neg_button.setObjectName("negativ")

        # removed samples
        self.removed_samples = QComboBox()

        # layouts
        # vertical box
        self.v_box = QtWidgets.QVBoxLayout()
        self.v_box.addWidget(self.table_source)
        self.v_box.addWidget(self.seach_bar)
        self.v_box.addWidget(self.pos_button)
        self.v_box.addWidget(self.neg_button)
        self.v_box.addWidget(self.table_widget)
        self.v_box.addWidget(QLabel("Restore samples"))
        self.v_box.addWidget(self.removed_samples)
        
        # barcodes
        self.barcode_df = pd.read_csv(barcodes)
        self.barcode_list = QListWidget()
        self.barcode_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.barcode_list.setDragEnabled(True)
        self.update_barcodes_to_barcodelist()  
        # how to change the size?
        #self.barcode_list.setMinimumWidth(40)

        
        # horizontal box
        self.h_box = QtWidgets.QHBoxLayout()
        self.h_box.addWidget(self.barcode_list)
        self.h_box.addLayout(self.v_box)
        
        # signals and slots
        self.seach_bar.textChanged.connect(self.update_search)
        self.pos_button.clicked.connect(self.add_row)
        self.neg_button.clicked.connect(self.add_row)
        self.removed_samples.activated.connect(self.restore_removed_samples)

        # counters
        self.pos_counter = 0
        self.neg_counter = 0

        # main widget
        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setLayout(self.h_box)
        self.setCentralWidget(self.main_widget)
        self.resize(1350, 750)

    def create_model(
        self, Model: QtCore.QAbstractTableModel, data: str
    ) -> QtCore.QAbstractItemModel:
        """Creates a model and returns it"""

        df = pd.read_csv(data)
        model = Model(df)
        return model

    # Signals and slots

    # TODO
    def update_search(self):
        self.source_model.setFilterWildcard(f"*{text}*")
        # update
        self.source_model.layoutChanged.emit()

    def add_row(self, text):
        name = self.sender().objectName()
        if name == "positiv":
            new_df = pd.DataFrame().assign(
                sample_id=[f"POS_NY_{self.pos_counter}"], order=[-1]
            )
            self.pos_counter += 1
        elif name == "negativ":
            new_df = pd.DataFrame().assign(
                sample_id=[f"NEG_NY_{self.neg_counter}"], order=[1]
            )
            self.neg_counter += 1

        self.source_model.addRow(new_df)
        self.add_data_to_plate_widget()

    def setup_table_widget(self):
        self.table_widget = QTableWidget(8, 12)
        v_header = [QTableWidgetItem(x) for x in "ABCDEFGH"]
        for i, v in enumerate(v_header):
            self.table_widget.setVerticalHeaderItem(i, v)
        header = self.table_widget.verticalHeader()
        header.setVisible(True)
        self.add_data_to_plate_widget()

    def add_data_to_plate_widget(self):
        self.table_widget.clearContents()
        number = 0
        for sample in self.source_model._data["sample_id"]:
            item = QTableWidgetItem(sample)
            # item should not be editable
            item.setFlags(~QtCore.Qt.ItemIsEditable)
            if "POS" in sample:
                item.setBackground(QtGui.QColor("#e5fab9"))
            elif "NEG" in sample:
                item.setBackground(QtGui.QColor("#fc9b90"))
            else:
                item.setBackground(QtGui.QColor("#b3d0ff"))

            self.table_widget.setItem(number % 8, number // 8, item)
            number += 1
            if number > 12 * 8:
                break

    def _hide_columns(self):
        """
        Hide columns from the TableViews
        """
        # hide order in both tables
        order = self.source_model.find_column_index("order")
        self.table_source.hideColumn(order)

    def add_removed_samples(self) -> None:
        """Adds the sample id to the View of removed items"""
        self.removed_samples.clear()
        for item in self.source_model.removed_samples_df["sample_id"]:
            self.removed_samples.addItem(item)

    def restore_removed_samples(self, sample_index: int) -> None:
        """Restore the chosen sample to the source model dataframe"""
        restore = self.source_model.removed_samples_df.iloc[
            sample_index : sample_index + 1
        ]
        self.source_model.addRow(restore)
        self.removed_samples.removeItem(sample_index)

        # drop the rows from the removed_samples_df
        self.source_model.removed_samples_df = (
            self.source_model.removed_samples_df
            .drop(index=sample_index)
            .reset_index(drop=True)
        )

        self.add_data_to_plate_widget()
        
    def update_barcodes_to_barcodelist(self):
        self.barcode_list.clear()
        for bc in self.barcode_df['bc']:
            self.barcode_list.addItem(bc)
            
            
def main():

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(model=PandasModel, 
                        data="new_test.csv",
                        barcodes='barcodes.csv')
    window.show()
    app.exec()


if __name__ == "__main__":
    main()