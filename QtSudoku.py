import sys
from copy import deepcopy

from PyQt5 import QtCore, QtWidgets

from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, \
    QPushButton, QVBoxLayout

from os import environ

import Sudoku as sd
from UIElements import Cell, Block



###############################################################################
# Allow HighDPI Scaling

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

###############################################################################


class SudokuMainWindow(QMainWindow):
    def __init__(self, board):#, cand_board):
        super(QMainWindow, self).__init__()

        board_layout, side_ui_layout = self.SetupWindow()

        # Variables (UI)
        self.cells = self.CreateBoard(self, board_layout)
        self.selected_cell = None

        # Create the msg text ui element to pass messages to user
        self.msgText = QLabel('Num Solutions: ?')
        self.msgText.setStyleSheet("border: 1px solid black;")
        side_ui_layout.addWidget(self.msgText)

        self.CreateButtons(self, side_ui_layout)

        # Variables (Data)
        self.orig_board = board
        self.curr_board = deepcopy(board)
        self.cand_board = None

        self.ResetBoard()

    def SetupWindow(self):
        # Setup Window - calls to QMainWindow methods (not overridden)
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
    def AddButton(layout, title, func):
        button = QPushButton(title)
        button.clicked.connect(func)
        layout.addWidget(button)

    @staticmethod
    def CreateBlock(parent, layout, bi, bj):
        block = Block(parent)
        layout.addWidget(block, bi, bj)
        return block

    @staticmethod
    def CreateCell(i, j, boxes, click_func):
        bi, bj = i // 3, j // 3
        parent_box = boxes[bi][bj]
        cell = Cell(parent_box, i, j)#, self.curr_board[i][j])
        cell.ConnectCelltoWindow(click_func)
        parent_box.AddCell(cell, i - 3 * bi, j - 3 * bj)
        return cell

    def CreateBoard(self, parent, layout):
        """ Creates board display with initial board values and candidates """
        # Create boxes for each 9x9 block
        blocks = [[self.CreateBlock(parent, layout, bi, bj) for bj in range(3)] for bi in range(3)]
        return [[self.CreateCell(i, j, blocks, self.CellClicked) for j in range(9)] for i in range(9)]

    def CreateButtons(self, parent, layout):
        """ Create the buttons toolbar for solving options """

        self.AddButton(layout, 'Restart', lambda: self.ResetBoard())
        self.AddButton(layout, 'Solve', lambda: self.Solve())
        self.AddButton(layout, 'Fill Single Candidates', lambda: self.FillinSingleCandidatesStep())
        # self.AddButton(layout, 'Fill Single Candidates', lambda: self.FillinSingleCandidates())
        self.AddButton(layout, 'Update Candidates', lambda: self.UpdatePossibleCandidates())
        self.AddButton(layout, 'Highlight Hidden Singles', lambda: self.HighlightHiddenSingles())
        self.AddButton(layout, 'Highlight Naked Pairs', lambda: self.HighlightNakedPairs())
        self.AddButton(layout, 'Highlight Pointing Pairs', lambda: self.HighlightPointingPairs())
        self.AddButton(layout, 'Highlight Box-Line Pairs', lambda: self.HighlightBoxLinePairs())
        self.AddButton(layout, 'Highlight Box Triples', lambda: self.HighlightBoxTriples())
        self.AddButton(layout, 'X-Wings', lambda: self.HighlightXWings())
        self.AddButton(layout, 'Re-generate Candidates', lambda: self.RegenerateCandidates())
        self.AddButton(layout, 'Clear Highlights', lambda: self.ClearHighlights())

    def RemoveCandidatesBasedonCellValue(self, i, j, value):
        """ If have assigned a value to cell i,j then remove the value as a
        candidates from the block, row and column of that cell """

        bi, bj = i // 3, j // 3
        block = [self.cells[bi * 3 + ci][bj * 3 + cj] for cj in range(0, 3) for ci in range(0, 3)]

        for cell in block:
            cell.RemoveCandidate(value)

        row_i = self.cells[i]
        for cell in row_i:
            cell.RemoveCandidate(value)

        col_j = [row[j] for row in self.cells]
        for cell in col_j:
            cell.RemoveCandidate(value)

    def ResetAllCellsValid(self):
        """ Remove indication of invalid cells """
        self.msgText.setStyleSheet("border: 1px solid black; color: black;")
        for i in range(0, 9):
            for j in range(0, 9):
                self.cells[i][j].SetValidity(is_invalid=False)

    def ShowInvalidCells(self, dups):
        """ Highlight cells that are a duplicate of that number in row, column
        or block.  List of duplicates passed in as list of tuple (i,j) pairs. """
        self.ResetAllCellsValid()
        for dup in dups:
            self.msgText.setStyleSheet("border: 1px solid black; color: red;")
            self.cells[dup[0]][dup[1]].SetValidity(is_invalid=True)

    def UpdateChangedCells(self, prevBoard):
        """ Update the display of changed cells and remove candidates that
        are no longer valid due to the new values filled in """
        for i in range(0, 9):
            for j in range(0, 9):
                if prevBoard[i][j] != self.curr_board[i][j]:
                    self.cells[i][j].UpdateValue(self.curr_board[i][j])
                    self.RemoveCandidatesBasedonCellValue(i, j, self.curr_board[i][j])

    def HighlightRemovals(self, rCands):
        """ Highlight candidates that can be removed based on list rCands """
        for rCand in rCands:
            n, i, j = rCand
            self.cells[i][j].HiliteCandidates(set([n]), colour='red')

    # Methods called by UI buttons

    def ResetBoard(self):
        self.curr_board = self.orig_board
        self.msgText.setStyleSheet("border: 1px solid black; color: black;")
        self.msgText.setText('Num Solutions: ?')

        for i in range(0, 9):
            for j in range(0, 9):
                self.cells[i][j].UpdateValue(self.curr_board[i][j], initial=True)

        self.RegenerateCandidates()

    def Solve(self):
        """ Solves the board using the backtracking alogorithm """
        if sd.BoardSolved(self.curr_board):
            return

        self.ClearHighlights()
        dups = sd.FindDuplicates(self.curr_board)

        num_solns = 0

        if sd.CheckValid(dups):
            prev_board = deepcopy(self.curr_board)

            print('Start Solver')
            num_solns, soln_board = sd.SolvewBacktrack(self.curr_board)
            print('End Solver')

            # Prob not needed but here as a failsafe
            dups = sd.FindDuplicates(self.curr_board)
            if not sd.CheckValid(dups):
                print('Invalid')
                num_solns = 0
            elif num_solns == 0:
                print('No solution')
            elif num_solns == 1:
                print('Single Solution')
                self.curr_board = soln_board
                self.UpdateChangedCells(prev_board)
            else:
                print('Multiple Solutions')

        self.ShowInvalidCells(dups)

        if num_solns == 1:
            self.msgText.setStyleSheet("border: 1px solid black; color: black;")
        else:
            self.msgText.setStyleSheet("border: 1px solid black; color: red;")

        self.msgText.setText('Num Solutions: ' + str(num_solns))

    def FillinSingleCandidatesStep(self):
        """ Look for cells with only 1 candidate and fill them in.
        Updates the candidates after finished """
        self.ClearHighlights()
        dups = sd.FindDuplicates(self.curr_board)
        if sd.CheckValid(dups):
            prev_board = deepcopy(self.curr_board)

            changed, self.curr_board, self.cand_board = sd.FillSingleCandidates(self.curr_board, self.cand_board)
            if changed:
                self.UpdateChangedCells(prev_board)

            dups = sd.FindDuplicates(self.curr_board)
            if not sd.CheckValid(dups):
                print('Invalid')

        self.ShowInvalidCells(dups)

    def FillinSingleCandidates(self):
        """ Look for cells with only 1 candidate and fill them in
        Then update candidates and iterate until no more changes """
        self.ClearHighlights()
        dups = sd.FindDuplicates(self.curr_board)
        if sd.CheckValid(dups):
            not_done = True

            prev_board = deepcopy(self.curr_board)

            while not_done:
                not_done, self.curr_board, self.cand_board = sd.FillSingleCandidates(self.curr_board, self.cand_board)

            self.UpdateChangedCells(prev_board)

            dups = sd.FindDuplicates(self.curr_board)
            if not sd.CheckValid(dups):
                print('Invalid')

        self.ShowInvalidCells(dups)

    def UpdatePossibleCandidates(self):
        """ Removes any candidates that are no longer valid.
        Does NOT reset candidate changes made previously """
        self.ClearHighlights()
        self.cand_board = sd.SolveCandidatesIntersect(self.curr_board, self.cand_board)

        for i in range(0, 9):
            for j in range(0, 9):
                cand_set = self.cand_board[i][j]
                self.cells[i][j].UpdateCandidates(cand_set)

    def HighlightHiddenSingles(self):
        """ Highlight where there are hidden single candidates """
        self.ClearHighlights()
        hidden_singles = sd.HiddenSingles(self.curr_board, self.cand_board)

        for hiddenSingle in hidden_singles:
            i, j, n = hiddenSingle
            self.cells[i][j].HiliteCandidates(set([n]))

    def HighlightNakedPairs(self):
        """ Highlight where there are naked pair candidates """
        self.ClearHighlights()
        pairSets, rCands = sd.NakedPairs(self.curr_board, self.cand_board)

        for pairSet in pairSets:
            a, b, i1, j1, i2, j2 = pairSet
            self.cells[i1][j1].HiliteCandidates(set([a, b]))
            self.cells[i2][j2].HiliteCandidates(set([a, b]))

        self.HighlightRemovals(rCands)

    def HighlightPointingPairs(self):
        """ Highlight where there are pointing pair candidates """
        self.ClearHighlights()

        pair_sets, rCands = sd.PointingPairs(self.curr_board, self.cand_board)

        for pairSet in pair_sets:
            n, i1, j1, i2, j2 = pairSet
            self.cells[i1][j1].HiliteCandidates(set([n]))
            self.cells[i2][j2].HiliteCandidates(set([n]))

        self.HighlightRemovals(rCands)

    def HighlightBoxLinePairs(self):
        """ Highlight where there are box-line pair candidates """
        self.ClearHighlights()
        pair_sets, rCands = sd.BoxLinePairs(self.curr_board, self.cand_board)

        for pairSet in pair_sets:
            n, i1, j1, i2, j2 = pairSet
            self.cells[i1][j1].HiliteCandidates(set([n]))
            self.cells[i2][j2].HiliteCandidates(set([n]))

        self.HighlightRemovals(rCands)

    def HighlightBoxTriples(self):
        """ Highlight where there are box triple candidates """
        self.ClearHighlights()
        triples, rCands = sd.BoxTriples(self.curr_board, self.cand_board)

        for trip in triples:
            print(trip)
            a, b, c, (i1, j1), (i2, j2), (i3, j3) = trip
            self.cells[i1][j1].HiliteCandidates(set([a, b, c]) & self.cand_board[i1][j1])
            self.cells[i2][j2].HiliteCandidates(set([a, b, c]) & self.cand_board[i2][j2])
            self.cells[i3][j3].HiliteCandidates(set([a, b, c]) & self.cand_board[i3][j3])

        self.HighlightRemovals(rCands)

    def HighlightXWings(self):
        self.ClearHighlights()
        xwings, rCands = sd.XWings(self.curr_board, self.cand_board)

        for xwing in xwings:
            print(xwing)
            n, (i1, j1), (i2, j2), (i3, j3), (i4, j4) = xwing
            self.cells[i1][j1].HiliteCandidates(set([n]) & self.cand_board[i1][j1])
            self.cells[i2][j2].HiliteCandidates(set([n]) & self.cand_board[i2][j2])
            self.cells[i3][j3].HiliteCandidates(set([n]) & self.cand_board[i3][j3])
            self.cells[i4][j4].HiliteCandidates(set([n]) & self.cand_board[i4][j4])

        self.HighlightRemovals(rCands)

    def RegenerateCandidates(self):
        """ Reset the displayed candidates to those based on those that are
        valid (ie avoid duplicates). Resets any candidate changes based on other
        patterns like hidden singles etc. """
        self.ClearHighlights()
        self.cand_board = sd.SolveCandidates(self.curr_board)

        for i in range(0, 9):
            for j in range(0, 9):
                cand_set = self.cand_board[i][j]
                self.cells[i][j].UpdateCandidates(cand_set)

    def ClearHighlights(self):
        """ Remove all highlight from candidatyes """
        for i in range(0, 9):
            for j in range(0, 9):
                self.cells[i][j].ClearHilites()

    # UI Events

    def mouseReleaseEvent(self, QMouseEvent):
        """ If mouse clicked not on child widget such as a cell """
        if self.selected_cell:
            self.selected_cell.Deselect()
        self.selected_cell = None
        print('(' + str(QMouseEvent.x()) + ', ' + str(QMouseEvent.y()) + ') \
              (' + str(self.width()) + ',' + str(self.height()) + ')')

    def keyPressEvent(self, event):
        """ Handles key presses.  If is a number key, update the value in selected
        cell  """
        key = event.key()
        key_str = event.text()

        if self.selected_cell and self.selected_cell.CanEdit():
            i, j = self.selected_cell.i, self.selected_cell.j

            # If number key pressed
            if QtCore.Qt.Key_1 <= key <= QtCore.Qt.Key_9 and self.curr_board[i][j] != int(key_str):
                self.selected_cell.UpdateValue(int(key_str))
                self.curr_board[i][j] = int(key_str)
            #                self.UpdatePossibleCandidates()

            if key == QtCore.Qt.Key_Backspace and self.curr_board[i][j] != 0:
                self.msgText.setText('Num Solutions: ?')
                self.selected_cell.UpdateValue(' ')
                self.curr_board[i][j] = 0

            dups = sd.FindDuplicates(self.curr_board)
            if not sd.CheckValid(dups):
                print('Invalid', dups)

            self.ShowInvalidCells(dups)

    def CellClicked(self, cell, cand):
        """ Handler function for a cell being clicked.  Makes sure only 1 cell
        is selected at a time ie only 1 cell has focus for input.
        cand is the number of the candidate clicked, if none was clicked then cand is zero
        cell is the Cell object that was clicked
        """
        if self.selected_cell and self.selected_cell is not cell:
            self.selected_cell.Deselect()

        self.selected_cell = cell

        if cand > 0:  # If candidate clicked then toggle it
            i, j = self.selected_cell.i, self.selected_cell.j
            if cand in self.cand_board[i][j]:
                self.cand_board[i][j].remove(cand)
            else:
                self.cand_board[i][j].add(cand)

        value_str = ', with value ' + self.selected_cell.text() if self.selected_cell else ''
        cand_str = ', changed candidate ' + str(cand) if cand > 0 else ''

        print('Clicked on cell (' + str(self.selected_cell.i) + ',' \
              + str(self.selected_cell.j) + ')' + value_str + cand_str)


###############################################################################
# Main App function - creates the app and window then passes control to the
# app GUI.  Returns when app quits

def run_app(orig_board):
    """ Main application function """
    print('Board is valid:', sd.BoardIsValid(orig_board))

    app = QtWidgets.QApplication(sys.argv)
    main_win = SudokuMainWindow(orig_board)
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
