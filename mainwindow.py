"""Main module."""

import sys
import pandas as pd
from pathlib import Path

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
    QFileDialog,
    QSpinBox,
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
from PySide6.QtGui import QAction, QShortcut, QKeySequence


import qtawesome as qta

from poresamplespandas.ui.mw import Ui_MainWindow
from poresamplespandas.widgets.tab_widget import TabMenu
from poresamplespandas.widgets.data_widget import DataWidget
from poresamplespandas.views.sample_table_view import SampleTableView
from poresamplespandas.import_data.import_analytix import import_analytix
from poresamplespandas.enums.enums import VERTICAL_HEADER
from poresamplespandas.import_data.import_barcodes import (
    make_barcodes_df,
    make_barcodes_df2,
)


VERSION = "PORESAMPLESPANDAS"


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, model: QtCore.QAbstractTableModel, data: str, barcodes: str):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.setWindowTitle(f"poresamples {VERSION}")
        self.setWindowIcon(qta.icon("mdi6.cube-outline"))

        # removed samples
        self.removed_samples = QComboBox()

        # barcodes
        self.barcode_file = barcodes
        self.barcode_df = make_barcodes_df2(self.barcode_file)

        # controls
        self.pos_spinbox = QSpinBox()
        self.pos_spinbox.setObjectName("POS")
        self.neg_spinbox = QSpinBox()
        self.neg_spinbox.setObjectName("NEG")

        # should barcodes go here or not??
        self.setup_action_buttons()
        self.populate_toolbar()

        # data widget, source model, sample table view and table widget
        self.input_model = model
        self.create_model(model=model, data=data)
        self.sample_table_view = SampleTableView(mainwindow=self)
        self.sample_table_view.setModel(self.source_model)
        self.setup_table_widget()
        self.datawidget = DataWidget(
            sample_table_view=self.sample_table_view,
            table_widget=self.table_widget,
            mainwindow=self,
        )

        # signals and slots
        self.pos_spinbox.valueChanged.connect(self.add_row_spinbox)
        self.neg_spinbox.valueChanged.connect(self.add_row_spinbox)
        self.removed_samples.activated.connect(self.restore_removed_samples)
        self.file_tab_signals()
        self.datawidget.refresh_barcodes.clicked.connect(self.refresh_barcodes)

        # shortcuts
        self.undo_barcode = None
        self.undo()
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.on_export)
        self.open_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        self.open_shortcut.activated.connect(self.on_import)

        # layout
        self.horizontalLayout.addWidget(self.tabWidget)
        self.horizontalLayout.addWidget(self.datawidget)
        self._hide_columns()

    def populate_toolbar(self):
        self.tabWidget = TabMenu(self)
        self.toolBar.addAction(self.sb_buttons["file"])
        self.toolBar.addAction(self.sb_buttons["barcode"])
        self.toolBar.addAction(self.sb_buttons["help"])
        self.toolBar.setMovable(False)

    def setup_action_buttons(self):
        self.sb_buttons = {
            "file": QAction("file", self),
            "barcode": QAction("barcode", self),
            "help": QAction("help", self),
        }

        self.sb_buttons["file"].setIcon(qta.icon("fa5.file"))
        self.sb_buttons["file"].setStatusTip("Files")
        self.sb_buttons["file"].setCheckable(True)
        self.sb_buttons["file"].triggered.connect(self.on_sb_button_click)

        self.sb_buttons["barcode"].setIcon(qta.icon("ri.barcode-fill", color="red"))
        self.sb_buttons["barcode"].setStatusTip("Barcodes")
        self.sb_buttons["barcode"].setCheckable(True)
        self.sb_buttons["barcode"].triggered.connect(self.on_sb_button_click)

        self.sb_buttons["help"].setIcon(qta.icon("fa5.question-circle", color="blue"))
        self.sb_buttons["help"].setStatusTip("help")
        self.sb_buttons["help"].setCheckable(True)
        self.sb_buttons["help"].triggered.connect(self.on_sb_button_click)

    def on_sb_button_click(self):
        action = self.sender()
        tab_name = action.text()
        self.tabWidget.open_tab(tab_name)

        for name, button in self.sb_buttons.items():
            if name != tab_name and button.isChecked():
                button.setChecked(False)

    # TODO add different importers
    def create_model(self, model: QtCore.QAbstractTableModel, data: str) -> None:
        """Creates a model and returns it"""
        if not isinstance(data, pd.DataFrame):
            data = pd.read_csv(data)
        self.source_model = model(data)

    def setup_table_widget(self):
        self.table_widget = QTableWidget(8, 12)
        # names of rows in the 96 plate well goes from A to H.
        v_header = [QTableWidgetItem(x) for x in "ABCDEFGH"]
        for i, v in enumerate(v_header):
            self.table_widget.setVerticalHeaderItem(i, v)
        header = self.table_widget.verticalHeader()
        header.setVisible(True)
        self.add_data_to_plate_widget()

    def add_row_spinbox(self, text):
        # helper function
        def add_controls(name):
            controls = []
            sort_order = -1 if name == "POS" else 1
            # clean the model dataframe from all controls
            self.source_model._data = self.source_model._data.loc[
                lambda x: ~x.sample_id.str.contains(name)
            ]
            # update the model to show correct dataframe
            self.source_model.sort()
            self.add_data_to_plate_widget()

            # Do not do anything if the user has not set the control to anything
            if int(text) == 0:
                return None

            for i in range(1, int(text) + 1):
                new_df = pd.DataFrame().assign(
                    sample_id=[f"{name}_CTRL{i}"],
                    order=[sort_order],
                    comment=[f"{name} Control"],
                )
                controls.append(new_df)
            self.source_model.addRow(pd.concat(controls))
            self.add_data_to_plate_widget()

        name = self.sender().objectName()
        add_controls(name)

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

            # truncated division and modulo for pushing the correct column
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
            self.source_model.removed_samples_df.drop(index=sample_index).reset_index(
                drop=True
            )
        )
        self.add_data_to_plate_widget()

    def file_tab_signals(self) -> None:
        self.tabWidget.button_import.clicked.connect(self.on_import)
        self.tabWidget.button_export.clicked.connect(self.on_export)

    def on_export(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save file",
            "/Users/wiro0005/Desktop",
            "csv file (*.csv)",
        )
        # filter and save the file
        (
            self.source_model._data.drop(columns=["order"])
            .assign(plate_position=lambda x: VERTICAL_HEADER[: x.shape[0]])
            .to_csv(filename, index=False)
        )

    def on_import(self):
        importers = {"analytix": import_analytix, "illumina": None}

        indata, _ = QFileDialog.getOpenFileName(
            self,
            "Open file",
            "/Users/wiro0005/Desktop",
            "analytix file (*.csv *.txt)",
        )

        if indata:
            filename = indata
            current_importer = importers[self.tabWidget.file_type.currentText()]
            indata = current_importer(Path(indata).resolve())

            # setup new data
            self.setup_new_data(indata, filename)

    def undo(self):
        self.sample_table_view.last_state()
        # remove the old
        if self.undo_barcode:
            self.undo_barcode.setParent(None)
            self.undo_barcode.deleteLater()
            self.undo_barcode = None
        self.undo_barcode = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.undo_barcode.activated.connect(self.sample_table_view.undo_barcodes)

    def setup_new_data(self, indata: pd.DataFrame, filename: str):
        """
        When reading in new data everything needs to be flushed and set up again
        """
        # create new models and sample views
        self.create_model(model=self.input_model, data=indata)
        self.sample_table_view = SampleTableView(mainwindow=self)
        self.sample_table_view.setModel(self.source_model)

        # delete the old data widget
        self.horizontalLayout.removeWidget(self.datawidget)
        # delete later was the key for removing the widget
        self.datawidget.deleteLater()
        self.datawidget = None

        # add new datawidgets and update things
        self.datawidget = DataWidget(
            sample_table_view=self.sample_table_view,
            table_widget=self.table_widget,
            mainwindow=self,
            name_of_file=filename,
        )
        self.horizontalLayout.addWidget(self.datawidget)
        self.add_data_to_plate_widget()
        self._hide_columns()
        self.removed_samples.clear()
        # update the last state so that ctrl z works

        # refresh barcodes
        self.refresh_barcodes()
        self.datawidget.refresh_barcodes.clicked.connect(self.refresh_barcodes)
        self.undo()

    def refresh_barcodes(self):
        """
        Refreshes and reloads barcodes. Starts everything over from scratch.
        """
        # remove all barcodes from model dataframe
        self.source_model._data = self.source_model._data.assign(barcodes=" ", kit=" ")
        self.source_model.sort()
        self.barcode_df = make_barcodes_df2(self.barcode_file)
        self.tabWidget.update_barcodes()
