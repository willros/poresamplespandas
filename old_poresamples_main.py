from old_poresamples import MainWindow
from PySide6.QtWidgets import QApplication
import qtvscodestyle as qtvsc
import sys
from pathlib import Path

from poresamplespandas.models.pandas_model import PandasModel

   
def main():
    app = QApplication(sys.argv)
    mw = MainWindow(model=PandasModel,
                    data='new_test.csv',
                    barcodes='barcodes.csv')

    stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.LIGHT_VS)
    extra = Path("poresamplespandas/rc/style_add.qss").read_text()
    app.setStyleSheet(stylesheet + extra)

    mw.show()
    app.exec()


if __name__ == "__main__":
    main()