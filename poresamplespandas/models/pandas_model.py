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


class PandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe"""

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = dataframe
        self._original_data = self._data.copy()

        self.v_header = [
            "A1",
            "B1",
            "C1",
            "D1",
            "E1",
            "F1",
            "G1",
            "H1",
            "A2",
            "B2",
            "C2",
            "D2",
            "E2",
            "F2",
            "G2",
            "H2",
            "A3",
            "B3",
            "C3",
            "D3",
            "E3",
            "F3",
            "G3",
            "H3",
            "A4",
            "B4",
            "C4",
            "D4",
            "E4",
            "F4",
            "G4",
            "H4",
            "A5",
            "B5",
            "C5",
            "D5",
            "E5",
            "F5",
            "G5",
            "H5",
            "A6",
            "B6",
            "C6",
            "D6",
            "E6",
            "F6",
            "G6",
            "H6",
            "A7",
            "B7",
            "C7",
            "D7",
            "E7",
            "F7",
            "G7",
            "H7",
            "A8",
            "B8",
            "C8",
            "D8",
            "E8",
            "F8",
            "G8",
            "H8",
            "A9",
            "B9",
            "C9",
            "D9",
            "E9",
            "F9",
            "G9",
            "H9",
            "A10",
            "B10",
            "C10",
            "D10",
            "E10",
            "F10",
            "G10",
            "H10",
            "A11",
            "B11",
            "C11",
            "D11",
            "E11",
            "F11",
            "G11",
            "H11",
            "A12",
            "B12",
            "C12",
            "D12",
            "E12",
            "F12",
            "G12",
            "H12",
        ]
        self.sortby = {"order": True, "sample_id": True}
        self.removed_samples_df = pd.DataFrame()
        self.sort()
        

    # drag and drop
    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def rowCount(self, parent=QModelIndex()) -> int:
        """Override method from QAbstractTableModel

        Return row count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return self._data.shape[0]
        return 0

    def columnCount(self, parent=QModelIndex()) -> int:
        """Override method from QAbstractTableModel

        Return column count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return self._data.shape[1]
        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        """
        Return data cell from the pandas DataFrame
        """
        if not index.isValid():
            return None

        if role == Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return str(self._data.iloc[index.row(), index.column()])

        if role == Qt.BackgroundRole:
            if index.row() in self.pos_rows:
                return QtGui.QColor("#e5fab9")
            elif index.row() in self.neg_rows:
                return QtGui.QColor("#fc9b90")
            else:
                return QtGui.QColor("#b3d0ff")

        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole
    ):
        """
        Return dataframe v_header as vertical header data and columns as horizontal header data.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self.v_header[section])

        return None

    def setData(self, index, value, role):
        if not index.isValid():
            return False

        self._data.iloc[index.row(), index.column()] = value
        self.sort()
        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        if index.column() in [self.find_column_index("comment")]:
            return (
                QtCore.Qt.ItemIsEnabled
                | QtCore.Qt.ItemIsSelectable
                | QtCore.Qt.ItemIsEditable
            )
        
        # flags for allowing dropped item etc. 
        return (QtCore.Qt.ItemIsEnabled 
                | QtCore.Qt.ItemIsSelectable 
                | Qt.ItemIsDragEnabled 
                | Qt.ItemIsDropEnabled 
        )

    def addRow(self, value):
        self._data = self._data.pipe(lambda x: pd.concat([x, value], ignore_index=True))
        self.sort()
        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
        self.layoutChanged.emit()

    def sort(self, index: int = None, role=None):
        if self.sortby:
            columns = [col for col in self.sortby.keys()]
            order = [x for x in self.sortby.values()]
            self._data = self._data.sort_values(columns, ascending=order).reset_index(
                drop=True
            )
            self.update_color_list()
            self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
            self.layoutChanged.emit()

    def update_color_list(self):
        self.pos_rows = self._data.loc[
            lambda x: x.sample_id.str.contains("POS")
        ].index.to_list()
        self.neg_rows = self._data.loc[
            lambda x: x.sample_id.str.contains("NEG")
        ].index.to_list()

    def find_column_index(self, col_name: str) -> int:
        """Find index of column with certain name and returns its position"""
        return self._data.columns.to_list().index(col_name)
