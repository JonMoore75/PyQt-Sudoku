import sys
from os import environ
from PyQt5 import QtCore, QtWidgets

import Sudoku as sd

from Controller import Controller
from SudokuModel import SudokuModel
from PyQtView import PyQtSudokuView


###############################################################################
# Allow HighDPI Scaling

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

###############################################################################
###############################################################################
# Main App function - creates the app and window then passes control to the
# app GUI.  Returns when app quits


def run_app(orig_board):
    """ Main application function """
    print('Board is valid:', sd.BoardIsValid(orig_board))

    model = SudokuModel(orig_board)

    app = QtWidgets.QApplication(sys.argv)
    main_win = PyQtSudokuView()
    controller = Controller(main_win, model)
    main_win.show()

    return app.exec_()


###############################################################################

def UnitTests():
    print('######### Unit Tests #############')
    testboard = [
        [7, 8, 0, 4, 0, 0, 1, 2, 0],
        [6, 0, 0, 0, 7, 5, 0, 0, 9],
        [0, 0, 0, 6, 0, 1, 0, 7, 8],
        [0, 0, 7, 0, 4, 0, 2, 6, 0],
        [0, 0, 1, 0, 5, 0, 9, 3, 0],
        [9, 0, 4, 0, 6, 0, 0, 0, 5],
        [0, 7, 0, 3, 0, 0, 0, 1, 2],
        [1, 2, 0, 0, 0, 7, 4, 0, 0],
        [0, 4, 9, 2, 0, 6, 0, 0, 7]
    ]

    ns, sb = sd.SolvewBacktrack(testboard)
    print('Num Solutions in Test Board, should be 1:', ns)

    testboard[4][4] = 3
    print('Check valid via Row Duplicate Test. Should be False:', sd.BoardIsValid(testboard))

    testboard[4][4] = 7
    print('Check valid via Col Duplicate Test. Should be False:', sd.BoardIsValid(testboard))

    testboard[4][4] = 5
    testboard[8][8] = 1
    print('Check valid via Block Duplicate Test. Should be False:', sd.BoardIsValid(testboard))

    ns, sb = sd.SolvewBacktrack(testboard)
    print('Num Solutions in Invalid Test Board, should be 0:', ns)

    testboard = [
        [7, 8, 0, 4, 0, 0, 1, 2, 0],
        [6, 0, 0, 0, 7, 5, 0, 0, 9],
        [0, 0, 0, 6, 0, 1, 0, 7, 8],
        [0, 0, 7, 0, 4, 0, 2, 6, 0],
        [0, 0, 1, 0, 5, 0, 9, 3, 0],
        [9, 0, 4, 0, 6, 0, 0, 0, 5],
        [0, 7, 0, 3, 0, 0, 0, 1, 2],
        [1, 2, 0, 0, 0, 0, 4, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    ns, sb = sd.SolvewBacktrack(testboard)
    print('Num Solutions in Incomplete Test Board, should be > 1:', ns)

    print('######### End Unit Tests #############')


###############################################################################

if __name__ == "__main__":
    UnitTests()

    easyboard = [
        [0, 8, 0, 0, 0, 0, 3, 5, 0],
        [5, 0, 4, 0, 8, 0, 1, 9, 0],
        [0, 3, 0, 0, 4, 0, 0, 2, 8],
        [0, 0, 0, 0, 0, 9, 6, 0, 0],
        [0, 6, 3, 0, 0, 0, 4, 0, 2],
        [0, 0, 0, 7, 0, 0, 0, 1, 3],
        [4, 2, 0, 3, 9, 0, 0, 0, 7],
        [3, 5, 6, 0, 0, 8, 0, 4, 0],
        [0, 0, 8, 0, 2, 4, 5, 0, 0]
    ]

    hardboard = [
        [0, 0, 0, 0, 0, 0, 4, 0, 0],
        [0, 0, 1, 0, 7, 0, 0, 9, 0],
        [5, 0, 0, 0, 3, 0, 0, 0, 6],
        [0, 8, 0, 2, 0, 0, 0, 0, 0],
        [7, 0, 0, 0, 0, 0, 9, 2, 0],
        [1, 2, 0, 6, 0, 5, 0, 0, 0],
        [0, 5, 0, 0, 0, 0, 0, 4, 0],
        [0, 7, 3, 9, 0, 8, 0, 0, 0],
        [6, 0, 0, 4, 5, 0, 2, 0, 0]
    ]

    vhardboard = [
        [5, 0, 0, 6, 0, 0, 0, 0, 0],
        [0, 6, 0, 0, 0, 3, 9, 0, 0],
        [9, 0, 0, 0, 4, 0, 0, 0, 1],
        [7, 1, 0, 0, 5, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 4, 0, 5],
        [0, 0, 0, 0, 2, 0, 7, 1, 3],
        [6, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 8, 2, 0, 0, 0, 6, 0],
        [0, 0, 3, 0, 0, 4, 0, 0, 7]
    ]

    xwingboard = [
        [6, 0, 0, 0, 9, 0, 0, 0, 7],
        [0, 4, 0, 0, 0, 7, 1, 0, 0],
        [0, 0, 2, 8, 0, 0, 0, 5, 0],
        [8, 0, 0, 0, 0, 0, 0, 9, 0],
        [0, 0, 0, 0, 7, 0, 0, 0, 0],
        [0, 3, 0, 0, 0, 0, 0, 0, 8],
        [0, 5, 0, 0, 0, 2, 3, 0, 0],
        [0, 0, 4, 5, 0, 0, 0, 2, 0],
        [9, 0, 0, 0, 3, 0, 0, 0, 4]
    ]

    tripboard= [
        [6, 8, 3, 1, 9, 5, 2, 4, 7],
        [5, 4, 9, 0, 0, 7, 1, 0, 0],
        [7, 1, 2, 8, 0, 0, 9, 5, 0],
        [8, 6, 0, 0, 0, 0, 0, 9, 0],
        [0, 9, 0, 0, 7, 8, 0, 0, 0],
        [0, 3, 0, 0, 0, 0, 0, 0, 8],
        [1, 5, 6, 4, 8, 2, 3, 7, 9],
        [3, 7, 4, 5, 0, 9, 8, 2, 0],
        [9, 2, 8, 7, 3, 0, 5, 0, 4]
    ]

    obsboard = [
        [0, 7, 0, 0, 0, 0, 9, 1, 6],
        [4, 5, 1, 3, 6, 9, 7, 8, 2],
        [0, 6, 9, 0, 0, 1, 3, 5, 4],
        [0, 0, 7, 0, 0, 6, 1, 0, 8],
        [0, 0, 8, 0, 0, 0, 6, 0, 0],
        [6, 0, 0, 1, 9, 8, 0, 0, 0],
        [0, 0, 6, 9, 0, 0, 8, 0, 0],
        [7, 8, 0, 6, 1, 2, 0, 3, 9],
        [9, 3, 0, 4, 8, 7, 0, 6, 1],
    ]
    sys.exit(run_app(xwingboard))
