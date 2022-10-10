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

class SampleTableView(QTableView):
    """Class for The View of the sample sheet"""

    def __init__(self, mainwindow):
        super(SampleTableView, self).__init__()
        vh = self.verticalHeader()
        vh.setContextMenuPolicy(Qt.CustomContextMenu)
        vh.customContextMenuRequested.connect(self.menu_delete_button)
        self.setSortingEnabled(False)
        self.main_window = mainwindow

        # Drag and drop
        self.setDropIndicatorShown(True)
        self.setAcceptDrops(True)
                

    def remove_and_store(self):
        """Removes highlighted rows from the view and stores them in the list of removed rows"""
        indexes = self.selectionModel().selectedRows()
        index_slice = (
            slice(indexes[0].row(), indexes[-1].row() + 1)
            if len(indexes) > 1
            else slice(indexes[0].row(), indexes[0].row() + 1)
        )
        rows_to_remove = self.model()._data.index[index_slice]

        # save the rows about to be removed
        self.model().removed_samples_df = (
            self.model()
            .removed_samples_df.pipe(
                lambda x: pd.concat([x, self.model()._data.iloc[rows_to_remove]])
            )
            .reset_index(drop=True)
        )

        # drop the rows from the model._data
        self.model()._data = (
            self.model()._data.drop(rows_to_remove).reset_index(drop=True)
        )

        # update the model and the plate view
        self.main_window.add_data_to_plate_widget()

        # add to the removed list
        self.main_window.add_removed_samples()

        # update the color for POS and NEG
        self.model().update_color_list()
        self.model().layoutChanged.emit()
        
        # remove the selected rows
        self.clearSelection()

    @Slot(QPoint)
    def menu_delete_button(self, pos):
        widget = self.sender()
        selected_items = self.selectionModel().selectedRows()
        if selected_items:
            context_menu = QMenu(self)
            delete_action = QAction("Delete", self)
            context_menu.addAction(delete_action)
            delete_action.triggered.connect(self.remove_and_store)
            context_menu.exec(widget.mapToGlobal(pos))

    def dragEnterEvent(self, e):
        mime = e.mimeData()
        if mime.hasText() or mime.hasFormat("application/x-qabstractitemmodeldatalist"):
            e.accept()
        else:
            e.ignore()

    # dropping barcodes
    def dropEvent(self, e): 
        indexes = e.source().selectionModel().selectedRows()
        index_slice = (
            slice(indexes[0].row(), indexes[-1].row())
            if len(indexes) > 1
            else slice(indexes[0].row(), indexes[0].row())
        )
        
        # to undo adding of the barcodes
        self.barcodes_before = self.main_window.barcode_df.copy()
        self.data_before = self.model()._data.copy()
        
        chosen_barcodes = self.main_window.barcode_df.loc[index_slice, 'bc'].to_list()
        chosen_kit = self.main_window.barcode_df.loc[index_slice, 'kit'].to_list()
    
        #row to start insert of the model
        to_index = self.indexAt(e.pos())
        model_row = to_index.row()
        
        # how many rows down
        number_of_rows = len(indexes) - 1 if len(indexes) > 1 else 0
        rows_to_add = slice(model_row, (model_row + number_of_rows))
        
        # add barcodes and kit to the model
        self.model()._data.loc[rows_to_add, 'barcodes'] = chosen_barcodes
        self.model()._data.loc[rows_to_add, 'kit'] = chosen_kit
        
        # remove barcodes from barcodes df 
        index_slice_drop = (
            slice(indexes[0].row(), indexes[-1].row() + 1)
            if len(indexes) > 1
            else slice(indexes[0].row(), indexes[0].row() + 1)
        )
    
        rows_to_remove = self.main_window.barcode_df.index[index_slice_drop]
        
        self.main_window.barcode_df = (self.main_window.barcode_df
                                       .drop(rows_to_remove)
                                       .reset_index(drop=True))
        
        # update the barcode list
        self.main_window.update_barcodes_to_barcodelist()
        
         # update the data 
        self.model().dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
        self.model().layoutChanged.emit()
        
        # Find the index and row of the QListWidgetItems:
        #barcode_row = e.source().currentIndex().row()
        
    def undo_barcodes(self):
        # change back the data and the barcodes
        self.model()._data = self.data_before
        self.main_window.barcode_df = self.barcodes_before

        # update the barcode list
        self.main_window.update_barcodes_to_barcodelist()

        # update the data 
        self.model().update_color_list()
        self.model().dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
        self.model().layoutChanged.emit()
        self.main_window.add_data_to_plate_widget()

