import sys
from os import environ
from PyQt5 import QtCore, QtWidgets

import sudoku as sd

from Controller import Controller
from SudokuModel import SudokuModel
from PyQtView import PyQtSudokuView
import sudoku_boards as sb


###############################################################################
# Allow HighDPI Scaling

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

###############################################################################
###############################################################################


def run_app(orig_board):
    """ Main application function - creates the app and window then passes control to the
    app GUI.  Returns when app quits """
    print('Board is valid:', sd.BoardIsValid(orig_board))

    model = SudokuModel(orig_board)

    app = QtWidgets.QApplication(sys.argv)
    main_win = PyQtSudokuView()
    controller = Controller(main_win, model)
    main_win.show()

    return app.exec_()


###############################################################################


def main():
    sys.exit(run_app(sb.medboard))


if __name__ == "__main__":
    main()
