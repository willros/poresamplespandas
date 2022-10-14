from mainwindow import MainWindow
from PySide6.QtWidgets import QApplication
import sys
from pathlib import Path

from poresamplespandas.models.pandas_model import PandasModel

   
def main():
    app = QApplication(sys.argv)
    mw = MainWindow(model=PandasModel,
                    data='config/new_test.csv',
                    barcodes='config/barcodes.yaml')
    mw.show()
    app.exec()


if __name__ == "__main__":
    main()