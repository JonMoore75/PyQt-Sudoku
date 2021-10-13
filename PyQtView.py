from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from UIElements import Cell, Block

from enum import Enum, auto


class Cmds(Enum):
    NUM = auto()
    DEL = auto()
    MOUSE = auto()
    CELLCLICK = auto()


class PyQtSudokuView(QMainWindow):
    def __init__(self, button_map):
        super(QMainWindow, self).__init__()

        # Maps to map commands, keys and functions
        self.key_table = {k: Cmds.NUM for k in range(QtCore.Qt.Key_0, QtCore.Qt.Key_9+1)}
        self.key_table.update({QtCore.Qt.Key_Backspace: Cmds.DEL})
        self.func_map = {}

        board_layout, side_ui_layout = self.SetupWindow()

        # Variables (UI)
        self.cells = self.CreateBoard(self, board_layout)

        # Create the msg text ui element to pass messages to user
        self.msgText = QLabel('Num Solutions: ?')
        self.msgText.setStyleSheet("border: 1px solid black;")
        side_ui_layout.addWidget(self.msgText)

        self.CreateButtons(self, side_ui_layout)

        # Create UI elements
        self.buttons = {}
        for cmd in button_map:
            title = button_map[cmd]
            self.buttons[cmd] = QPushButton(title)
            side_ui_layout.addWidget(self.buttons[cmd])

            # Need to use this form of lambda to get local copy of button variable
            # otherwise button will be last value in the list for ALL buttons
            # lambda's (or local functions) use value at call time NOT creation!
            # See https://stackoverflow.com/questions/10452770/python-lambdas-binding-to-local-values
            self.buttons[cmd].clicked.connect(lambda state, x=cmd: self.ExecuteCmd(x))

    def SetupWindow(self):
        """ Setup Window - calls to QMainWindow methods (not overridden) """
        self.setGeometry(500, 30, 1200, 900)
        self.setWindowTitle("Simple Sudoku")
        self.setStyleSheet("background-color: grey;")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create UI layouts
        outer_layout = QGridLayout()
        board_layout = QGridLayout()
        side_ui_layout = QVBoxLayout()
        central_widget.setLayout(outer_layout)

        # Create layouts for sudoku board and side UI buttons on 12 x 9 UI grid
        # Sudoku board 9x9 on the UI grid, side UI 3 columns wide and 4 high (3rd to 6th row)
        outer_layout.addLayout(board_layout, 0, 0, 9, 9)
        outer_layout.addLayout(side_ui_layout, 2, 9, 4, 3)

        return board_layout, side_ui_layout

    @staticmethod
    def CreateBlock(parent, layout, bi, bj):
        block = Block(parent)
        layout.addWidget(block, bi, bj)
        return block

    @staticmethod
    def CreateCell(i, j, boxes, click_func):
        bi, bj = i // 3, j // 3
        parent_box = boxes[bi][bj]
        cell = Cell(parent_box, i, j)
        cell.ConnectCelltoWindow(click_func)
        parent_box.AddCell(cell, i - 3*bi, j - 3*bj)
        return cell

    def CreateBoard(self, parent, layout):
        """ Creates board display with initial board values and candidates """
        # Create boxes for each 9x9 block
        blocks = [[self.CreateBlock(parent, layout, bi, bj) for bj in range(3)] for bi in range(3)]
        return [[self.CreateCell(i, j, blocks, self.CellClicked) for j in range(9)] for i in range(9)]

    ####################################################################################################################

    def ExecuteCmd(self, cmd, data=None):
        """ Takes a command enum code and calls the corresponding function """
        if cmd in self.func_map:
            if data is not None:
                self.func_map[cmd](data)
            else:
                self.func_map[cmd]()

    def Connect(self, func_map):
        """ Allows other class (eg model or controller etc) to specify what function to call for each command """
        self.func_map = func_map

    def keyPressEvent(self, event):
        """ Handles key presses."""
        key = event.key()

        if key in self.key_table:
            cmd = self.key_table[key]
            if QtCore.Qt.Key_0 <= key <= QtCore.Qt.Key_9:
                num = int(key) - int(QtCore.Qt.Key_0)
                self.ExecuteCmd(cmd, num)
            else:
                self.ExecuteCmd(cmd)

    def mouseReleaseEvent(self, QMouseEvent):
        """ If mouse clicked NOT on child widget such as a cell """
        print('(' + str(QMouseEvent.x()) + ', ' + str(QMouseEvent.y()) + ') \
              (' + str(self.width()) + ',' + str(self.height()) + ')')

        self.ExecuteCmd(Cmds.MOUSE)

    def CellClicked(self, cell, cand):
        """ Handler function for a cell being clicked.  Pass onto Controller to handle """

        self.ExecuteCmd(Cmds.CELLCLICK, cell)

    ####################################################################################################################

    def ResetAllCellsValid(self):
        """ Remove indication of invalid cells """
        for i in range(0, 9):
            for j in range(0, 9):
                self.cells[i][j].SetValidity(is_invalid=False)

    def ShowInvalidCells(self, duplicate_cells):
        """ Highlight cells that are a duplicate of that number in row, column
        or block.  List of cell coord passed in as list of tuple (i,j) pairs. """
        self.ResetAllCellsValid()
        for cell in duplicate_cells:
            self.cells[cell[0]][cell[1]].SetValidity(is_invalid=True)

    ####################################################################################################################

    def UpdateAllCells(self, board, initial=False):
        """ Update all cells """
        for i in range(0, 9):
            for j in range(0, 9):
                self.cells[i][j].UpdateValue(board[i][j], initial)

    def UpdateAllCandidates(self, cand_board):
        """ Update all candidates in unfilled cells """
        for i in range(0, 9):
            for j in range(0, 9):
                self.cells[i][j].UpdateCandidates(cand_board[i][j])

    ####################################################################################################################

    def ClearHighlights(self):
        """ Remove all highlight from candidates """
        for i in range(0, 9):
            for j in range(0, 9):
                self.cells[i][j].ClearHilites()

    def HighlightRemovals(self, candidates, cells):
        """ Highlight candidates that can be removed based on list rCands """
        for cell_coords in cells:
            i, j = cell_coords
            self.cells[i][j].HiliteCandidates(candidates, colour='red')

    def HighlightValues(self, candidates, cells):
        """ Highlight candidates """
        for cell_coords in cells:
            i, j = cell_coords
            self.cells[i][j].HiliteCandidates(candidates)

    ####################################################################################################################

    def SetNumSolutions(self, num_solns):
        """ Sets the message area text """
        if num_solns == 1 or num_solns is None:
            self.msgText.setStyleSheet("border: 1px solid black; color: black;")
        else:
            self.msgText.setStyleSheet("border: 1px solid black; color: red;")

        if num_solns is None:
            self.msgText.setText('Num Solutions: ' + '?')
        elif num_solns < 0:
            self.msgText.setText('Num Solutions: ' + 'Board Invalid')
        else:
            self.msgText.setText('Num Solutions: ' + str(num_solns))

