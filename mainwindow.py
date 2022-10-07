"""Main module."""

import sys
import pandas as pd
from pathlib import Path
import yaml

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
    QMainWindow,
    QFileDialog
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

import qtawesome as qta

from poresamplespandas.ui.mw import Ui_MainWindow
from poresamplespandas.widgets.tab_widget import TabMenu
from poresamplespandas.widgets.data_widget import DataWidget
from poresamplespandas.views.sample_table_view import SampleTableView
from poresamplespandas.import_data.import_analytix import import_analytix

VERSION = "PORESAMPLESPANDAS"

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, 
                 model: QtCore.QAbstractTableModel,
                 data: str,
                 barcodes: str):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.setWindowTitle(f"poresamples {VERSION}")
        self.setWindowIcon(qta.icon("mdi6.cube-outline"))
        
        # removed samples
        self.removed_samples = QComboBox()
        
        # barcodes
        self.barcode_df = pd.read_csv(barcodes)
        self.barcode_list = QListWidget()
        self.barcode_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.barcode_list.setDragEnabled(True)
        self.update_barcodes_to_barcodelist()  
        self.barcode_list.setMinimumWidth(40)

        # buttons
        self.pos_button = QtWidgets.QPushButton("Positive")
        self.pos_button.setObjectName("positiv")
        self.pos_counter = 0
        self.neg_button = QtWidgets.QPushButton("Negative")
        self.neg_button.setObjectName("negativ")
        self.neg_counter = 0
        self.setup_action_buttons()
        # should barcodes go here or not??
        self.populate_toolbar()
        
        # signals and slots
        self.pos_button.clicked.connect(self.add_row)
        self.neg_button.clicked.connect(self.add_row)
        self.removed_samples.activated.connect(self.restore_removed_samples)
        self.file_tab_signals()
        
        # data widget, source model, sample table view and table widget
        self.create_model(model=model, data=data)
        self.sample_table_view = SampleTableView(mainwindow=self)
        self.sample_table_view.setModel(self.source_model)
        self.setup_table_widget()
        self.datawidget = DataWidget(sample_table_view=self.sample_table_view,
                                     table_widget=self.table_widget,
                                     mainwindow=self)
        
        # layout 
        self.horizontalLayout.addWidget(self.tabWidget)
        self.horizontalLayout.addWidget(self.datawidget)
        self._hide_columns()

    def populate_toolbar(self):
        self.tabWidget = TabMenu(self.barcode_list)
        self.toolBar.addAction(self.sb_buttons["file"])
        self.toolBar.addAction(self.sb_buttons["barcode"])
        self.toolBar.setMovable(False)

    def setup_action_buttons(self):
        self.sb_buttons = {
            "file": QAction("file", self),
            "barcode": QAction("barcode", self),
        }
        self.sb_buttons["file"].setIcon(qta.icon("fa5.file"))
        self.sb_buttons["file"].setStatusTip("Files")
        self.sb_buttons["file"].setCheckable(True)
        self.sb_buttons["file"].triggered.connect(self.on_sb_button_click)

        self.sb_buttons["barcode"].setIcon(qta.icon("ri.barcode-fill"))
        self.sb_buttons["barcode"].setStatusTip("Barcodes")
        self.sb_buttons["barcode"].setCheckable(True)
        self.sb_buttons["barcode"].triggered.connect(self.on_sb_button_click)


    def on_sb_button_click(self):
        action = self.sender()
        tab_name = action.text()
        self.tabWidget.open_tab(tab_name)

        for name, button in self.sb_buttons.items():
            if name != tab_name and button.isChecked():
                button.setChecked(False)
    
    # TODO add different importers 
    def create_model(
        self, 
        model: QtCore.QAbstractTableModel, 
        data: str
        ) -> None:
        """Creates a model and returns it"""
        
        # add different importers
        df = pd.read_csv(data)
        self.source_model = model(df)
    
    def setup_table_widget(self):
        self.table_widget = QTableWidget(8, 12)
        v_header = [QTableWidgetItem(x) for x in "ABCDEFGH"]
        for i, v in enumerate(v_header):
            self.table_widget.setVerticalHeaderItem(i, v)
        header = self.table_widget.verticalHeader()
        header.setVisible(True)
        self.add_data_to_plate_widget()

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
        order = self.source_model.find_column_index("order")
        self.sample_table_view.hideColumn(order)

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

    def file_tab_signals(self):
        #self.tabWidget.button_import.clicked.connect(self.on_import)
        #self.tabWidget.button_save.clicked.connect(self.on_save)
        #self.tabWidget.button_open.clicked.connect(self.on_open)
        #self.tabWidget.button_close.clicked.connect(self.on_close)
        self.tabWidget.button_export.clicked.connect(self.on_export)

    
    # functions for setup_signals
    def on_export(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save file",
            "/Users/wiro0005/Desktop",
            "csv file (*.csv)",
        )
        # filter and save the file
        (self.source_model._data
         .drop(columns=['order'])
         .to_csv(filename, index=False)
        )


#    # this can be more generalized and rewritten
#    def on_import(self):
#        indata, _ = QFileDialog.getOpenFileName(
#            self,
#            "Open file",
#            "C:/Dev/PyCharmProjects/poresamples/demo",
#            "analytix file (*.csv *.txt)",
#        )
#        if indata:
#            # The chosen module (e.g. analytix)
#            name = self.tabWidget.chosen_module.currentText()
#
#            importer = importlib.import_module(
#                f"modules.importers.{name}.importer"
#            ).Importer()
#
#            df = self.adjuster.prepare(importer.load(indata))
#
#            if isinstance(df, pd.DataFrame):
#                self.setup_data(df)
#            else:
#                print("DANGER DANGER!!!!!! PANIC!!")
#
#    def on_save(self):
#        r_count = self.model.rowCount()
#        c_count = self.model.columnCount()
#        data = {}
#
#        for c in range(c_count):
#            field = self.model.headerData(c, Qt.Horizontal, Qt.DisplayRole)
#            _col_data = []
#            for r in range(r_count):
#                idx = self.model.index(r, c)
#                _col_data.append(self.model.data(idx, Qt.DisplayRole))
#
#            data[field] = _col_data
#
#        df = pd.DataFrame(data)
#
#        print(df.to_string())
#
#        fname, _ = QFileDialog.getSaveFileName(
#            self,
#            "Save data",
#            "C:/Dev/PyCharmProjects/poresamples/demo",
#            "pickle file (*.pkl)",
#        )
#
#        if fname:
#            df.to_pickle(fname)
#
#    def on_open(self):
#        filename, _ = QFileDialog.getOpenFileName(
#            self,
#            "Open file",
#            "C:/Dev/PyCharmProjects/poresamples/demo",
#            "data pickle (*.pkl)",
#        )
#
#        if not filename:
            #return None

#        df = pd.read_pickle(fname)
         # clear the barcodes, plate and Everything! 
         # set everything up again, with models and data and barcodes? 
#        self.setup_data(df)
#
