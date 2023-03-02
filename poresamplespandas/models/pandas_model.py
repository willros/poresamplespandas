import pandas as pd
from natsort import natsort_keygen


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
    QListWidgetItem,
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

from ..enums.enums import VERTICAL_HEADER


class PandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe"""

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = dataframe
        self._original_data = self._data.copy()

        self.v_header = VERTICAL_HEADER
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
        return True

    def flags(self, index):
        if index.column() in [self.find_column_index("comment")]:
            return (
                QtCore.Qt.ItemIsEnabled
                | QtCore.Qt.ItemIsSelectable
                | QtCore.Qt.ItemIsEditable
            )

        # flags for allowing dropped item etc.
        return (
            QtCore.Qt.ItemIsEnabled
            | QtCore.Qt.ItemIsSelectable
            | Qt.ItemIsDragEnabled
            | Qt.ItemIsDropEnabled
        )

    def addRow(self, value):
        self._data = self._data.pipe(
            lambda x: pd.concat([x, value], ignore_index=True)
        ).fillna(" ")
        self.sort()

        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
        self.layoutChanged.emit()

    def sort(self, index: int = None, role=None):
        if self.sortby:
            columns = [col for col in self.sortby.keys()]
            order = [x for x in self.sortby.values()]
            self._data = self._data.sort_values(
                columns, ascending=order, key=natsort_keygen()
            ).reset_index(drop=True)
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
