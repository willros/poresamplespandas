"""Main module."""

import sys
import importlib
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QSizePolicy,
    QFileDialog,
    QLabel,
)
from PySide6.QtGui import QAction
from pathlib import Path
import yaml

import qtawesome as qta

from poresamplespandas.ui.mw import Ui_MainWindow
from poresamplespandas.widgets.tab_widget import TabMenu
from poresamplespandas.widgets.data_widget import DataWidget

VERSION = "PORESAMPLESPANDAS"


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, barcodes):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.setWindowTitle(f"poresamples {VERSION}")
        self.setWindowIcon(qta.icon("mdi6.cube-outline"))

        self.setup_action_buttons()
        self.populate_toolbar(barcodes)
#        self.datawidget = DataWidget()
#        self.model = CustomStandardItemModel()
#        self.setup_signals()
#
#        self.horizontalLayout.addWidget(self.tabWidget)
#        self.horizontalLayout.addWidget(self.datawidget)
#        self.horizontalLayout.addWidget(self.datawidget)
#
#    def setup_data(self, df):
#        self.model.populate(df)
#        fields = list(df.columns)
#
#        self.all_filterproxy = CtrlProxyModel(fields.index("visible_all"))
#        self.all_filterproxy.setSourceModel(self.model)
#
#        self.present_sample_filterproxy = CtrlProxyModel(
#            fields.index("visible_samples")
#        )
#        self.present_sample_filterproxy.setSourceModel(self.all_filterproxy)
#
#        self.removed_sample_filterproxy = CtrlProxyModel(
#            fields.index("visible_samples")
#        )
#        self.removed_sample_filterproxy.setSourceModel(self.all_filterproxy)
#
#        
#        self.custom_sortproxy = MultiSortFilterProxy(fields.index("order"))
#        self.custom_sortproxy.setSourceModel(self.present_sample_filterproxy)
#
#        self.plate_viewproxy = PlateProxy(fields.index("sample_id"))
#        self.plate_viewproxy.setSourceModel(self.custom_sortproxy)
#
#        self.datawidget.set_data(
#            fields,
#            self.custom_sortproxy,
#            self.plate_viewproxy,
#            self.removed_sample_filterproxy,
#            self.adjuster.pos_control_count,
#            self.adjuster.neg_control_count,
#            self.config["hidden_fields"],
#        )
#
    def populate_toolbar(self, barcodes):
        
        self.tabWidget = TabMenu(barcodes)

        self.toolBar.addAction(self.sb_buttons["file"])
        self.toolBar.addAction(self.sb_buttons["barcode"])
        self.toolBar.addAction(self.sb_buttons["settings"])

        self.toolBar.setMovable(False)

#
    def setup_action_buttons(self):

        self.sb_buttons = {
            "file": QAction("file", self),
            "barcode": QAction("barcode", self),
            "settings": QAction("settings", self),
        }

        self.sb_buttons["file"].setIcon(qta.icon("fa5.file"))
        self.sb_buttons["file"].setStatusTip("Files")
        self.sb_buttons["file"].setCheckable(True)
        self.sb_buttons["file"].triggered.connect(self.on_sb_button_click)

        self.sb_buttons["barcode"].setIcon(qta.icon("ri.barcode-fill"))
        self.sb_buttons["barcode"].setStatusTip("Barcodes")
        self.sb_buttons["barcode"].setCheckable(True)
        self.sb_buttons["barcode"].triggered.connect(self.on_sb_button_click)

        self.sb_buttons["settings"].setIcon(qta.icon("ei.cogs"))
        self.sb_buttons["settings"].setStatusTip("Settings")
        self.sb_buttons["settings"].setCheckable(True)
        self.sb_buttons["settings"].triggered.connect(self.on_sb_button_click)

    def on_sb_button_click(self):
        action = self.sender()
        tab_name = action.text()
        self.tabWidget.open_tab(tab_name)

        for name, button in self.sb_buttons.items():
            if name != tab_name and button.isChecked():
                button.setChecked(False)

#    def setup_signals(self):
#        # file tab
#        self.tabWidget.button_import.clicked.connect(self.on_import)
#        self.tabWidget.button_save.clicked.connect(self.on_save)
#        self.tabWidget.button_open.clicked.connect(self.on_open)
#        self.tabWidget.button_close.clicked.connect(self.on_close)
#        self.tabWidget.button_export.clicked.connect(self.on_export)
#
#        # settings tab
#        # TODO
#
#    # functions for setup_signals
#
#    def on_export(self):
#        print("OMFG")
#
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
#        fname, _ = QFileDialog.getOpenFileName(
#            self,
#            "Open file",
#            "C:/Dev/PyCharmProjects/poresamples/demo",
#            "data pickle (*.pkl)",
#        )
#
#        if fname:
#            df = pd.read_pickle(fname)
#            self.setup_data(df)
#
#    def on_close(self):
#        # remove this??
#        self.model = CustomStandardItemModel()
#
#        self.horizontalLayout.removeWidget(self.datawidget)
#        self.datawidget.deleteLater()
#        self.datawidget = DataWidget()
#        self.horizontalLayout.insertWidget(1, self.datawidget)
#
