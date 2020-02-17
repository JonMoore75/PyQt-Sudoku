import sys
from copy import deepcopy
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
Signal, Slot = pyqtSignal, pyqtSlot 
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, \
    QPushButton, QHBoxLayout, QVBoxLayout    

from PyQt5.QtGui import QFont

from os import environ

###############################################################################

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    
environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

###############################################################################
# Sudoku Model - These functions deal with the board, its candidates and 
# solutions 

def checkListForDuplicates(listOfElems):
    """ Check if given list contains any duplicates """
    return len(listOfElems) != len(set(listOfElems))

def FindRowDuplicates(board):
    """ If any duplicates numbers by row return location as (i,j) pairs """
    duplicates= []
    
    for i in range(0,9):
        row_i = board[i]
        for n in range(1,10):
            if row_i.count(n) > 1:
                duplicates += [(i,j) for j,x in enumerate(board[i]) if x == n]
        
    return duplicates
            
def FindColDuplicates(board):
    """ If any duplicates numbers by column return location as (i,j) pairs """    
    duplicates= []
    
    for j in range(0,9):
        col_j = [row[j] for row in board]
        for n in range(1,10):
            if col_j.count(n) > 1:
                duplicates += [(i,j) for i,x in enumerate(col_j) if x == n]
    
    return duplicates
    
def FindBlockDuplicates(board):
    """ If any duplicates numbers by block return location as (i,j) pairs """
    duplicates= []
    
    for b in range(0,9):
        bi, bj = b/3, b%3
        block = [board[bi*3 + ci][bj*3 + cj] for ci in range(0,3) for cj in range(0,3)]

        for n in range(1,10):
            if block.count(n) > 1:
                duplicates += [(3*bi+k/3,3*bj+k%3) for k,x in enumerate(block) if x == n]
            
    return duplicates

def FindDuplicates(board):
    """ Find duplicate entries on any row, column or block """
    return FindRowDuplicates(board) + \
        FindColDuplicates(board) + \
        FindBlockDuplicates(board)  
        
def CheckValid(dup):
    return len(dup) == 0

def RemoveZeros(inputList):
    """ Remove zeros from a list, returns only non-zero values """
    return list(filter(lambda a: a != 0, inputList))

def GetCandidateList(board, i, j):
    """ Find possible values in a cell """
    bi = i/3
    bj = j/3
    
    block = [[board[bi*3 + ci][bj*3 + cj] for cj in range(0,3)] for ci in range(0,3)]
    row_i = board[i]
    col_j = [row[j] for row in board]
    
    blockValues = set(RemoveZeros([c for row in block for c in row]))
    rowValues = set(RemoveZeros(row_i))
    colValues = set(RemoveZeros(col_j))
    
    return set(range(1,10)) - blockValues - rowValues - colValues

def FillSingleCandidates(board, candBoard):
    """ Fills in any empty cells with single candidate 
    Copies inputs so not changed by this function."""
    boardcopy = deepcopy(board)
    changed = False
    
    for i in range(0,9):
        for j in range(0,9): 
            if len(candBoard[i][j]) == 1 and board[i][j] == 0:
                changed = True
                boardcopy[i][j] = next(iter(candBoard[i][j]))
    
    return changed, boardcopy, SolveCandidates(boardcopy)

def SolveCandidates(board):
    """ Takes a Sudoku board (2d 9x9 list of ints with 0 as empty cell) and 
    returns a board that is a 2d 9x9 list of sets.  Each set is the possible 
    int values. Known values are now sets with 1 item. """
    candBoard = deepcopy(board)
    for i in range(0,9):
        for j in range(0,9):
            if board[i][j] == 0:
                candBoard[i][j] = GetCandidateList(board, i, j)
            else:
                candBoard[i][j] = set([board[i][j]])
    return candBoard

def FindEmpty(board):
    """ Find the first cell that is unknown empty """
    for i in range(0,9):
        for j in range(0,9):
            if board[i][j] == 0:
                return (i,j)
    return None

def SolvewBacktrack(board):
    """ Solve the puzzle via the backtracking algorithm """
    foundEmpty = FindEmpty(board)
    
    if not foundEmpty:
        return True # Solved!
    
    i,j = foundEmpty
    candSet = GetCandidateList(board, i, j)
    
    for cand in iter(candSet):
        
        board[i][j] = cand
        
        if SolvewBacktrack(board):
            return True
        
        board[i][j] = 0
        
    return False

###############################################################################
# View - this is the pyQT5 GUI dealing with input and display

def Value2String(value):
    return str(value) if value is not 0 else ' '
        
#####################      
  
class Cell(QLabel):
    selected = Signal(object)
    def __init__(self, parent, strValue, candSet, i, j):
        super(QLabel, self).__init__(strValue, parent)
        self.cellString = strValue
        self.i = i
        self.j = j

        self.setStyleSheet("""
           Cell[selected="true"] {background-color: lightblue;}
           Cell[selected="false"] {background-color: white;}
           Cell[edit="true"] {color: darkgrey;}
           Cell[edit="false"] {color: black;}
           Cell[invalid="true"] {color: red;}
            """)
        self.setProperty('selected', False)
        if strValue == ' ':
            self.setProperty('edit', True)
        else:
            self.setProperty('edit', False)
        self.style().unpolish(self)
        self.style().polish(self)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.cellfont = QFont("Arial", 45, QFont.Bold) 
        self.candidatefont = QFont("Arial", 12)

        self.setFont(self.cellfont)
        
        self.gridLayoutBox = QGridLayout() 
        self.setLayout(self.gridLayoutBox)
        
        if self.cellString == ' ':
            self.CreateCandidates(candSet)
            
    def CreateCandidates(self, candSet=set()): 
        """ Create grid of QLabel widgets to display the candidates """
        for i in range(0,3):
            for j in range(0,3):
                candValue = 3*i + j + 1
                candStr = str(candValue) if candValue in candSet else ' '
                candLabel = QLabel(candStr, self)
                candLabel.setFont(self.candidatefont)
                candLabel.setAttribute(Qt.WA_TranslucentBackground)
                self.gridLayoutBox.addWidget(candLabel, i, j)
                    
    def ConnectCelltoWindow(self, ClickFunc):
        self.selected.connect(ClickFunc)
        
    def CanEdit(self):
        return self.property('edit')
        
    def SetValidity(self, isInvalid):
        self.setProperty('invalid', isInvalid)
        self.style().unpolish(self)
        self.style().polish(self) 
        
                   
    def UpdateValue(self, strValue):
        """ Will fill in value in a cell if it is empty/unknown """
        if self.CanEdit(): 
            if strValue != ' ':
                # Delete all candidate label widgets 
                for i in reversed(range(self.gridLayoutBox.count())): 
                    self.gridLayoutBox.itemAt(i).widget().setParent(None)
            else:
                self.CreateCandidates()
                    
            self.setText(strValue)
            self.cellString = strValue

            
    def UpdateCandidates(self, candSet):
        """ Updates the valid candidates for empty/unknown cell """
        if self.cellString == ' ': 
            for i in range(0,3):
                for j in range(0,3):
                    candValue = 3*i + j + 1
                    candStr = str(candValue) if candValue in candSet else ' '
                    cand = self.gridLayoutBox.itemAtPosition(i, j).widget()
                    cand.setText(candStr)
                    
    def RemoveCandidate(self, value):
        """ Removes candidate value from empty/unknown cell """
        if self.cellString == ' ': 
            ri, rj = (value-1)/3, (value-1) % 3
            cand = self.gridLayoutBox.itemAtPosition(ri, rj).widget()
            cand.setText(' ')
                    
    def ToggleCandidateNumber(self, i,j): 
        """ Toggles the candidate number if under the mouse """                   
        candValue = 3*i + j + 1
        cand = self.gridLayoutBox.itemAtPosition(i, j).widget()
        if cand.underMouse():
            print candValue, cand.text()
            candStr = str(candValue) if cand.text() == ' ' else ' '
            cand.setText(candStr)
        
    def mouseReleaseEvent(self, QMouseEvent):
        """ Handle cell being clicked on """
        self.selected.emit(self)
        
        if self.property('selected') and self.cellString == ' ':
            for i in range(0,3):
                for j in range(0,3):
                    self.ToggleCandidateNumber(i,j)
        else: # Hightlight the cell in blue
            self.setProperty('selected', True)
            self.style().unpolish(self)
            self.style().polish(self)
    
    def Deselect(self):
        """ If cell selected, deselect it """
        self.setProperty('selected', False)
        self.style().unpolish(self)
        self.style().polish(self)
        
#####################      
        
class Box(QLabel):
    def __init__(self, parent, board, candBoard, bi, bj):
        super(QLabel, self).__init__(parent)
        self.setStyleSheet('background-color: lightgrey;')
                
        self.gridLayoutBox = QGridLayout() 
        self.setLayout(self.gridLayoutBox) 

    def AddCell(self, cellQLabel, i, j):
         self.gridLayoutBox.addWidget(cellQLabel, i, j)
                
#####################      
     
class SudokuMainWindow(QMainWindow):
    def __init__(self, board, candBoard):
        super(QMainWindow, self).__init__()
        
        # Variables
        self.origBoard = board
        self.currBoard = deepcopy(board)
        self.candBoard = deepcopy(candBoard)
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        self.selectedCell = None
        
        # Setup function calls
        
        # Setup Window
        self.setGeometry(500, 30, 1200, 900)    
        self.setWindowTitle("Simple Sudoku") 
        self.setStyleSheet("background-color: grey;")
        
        # Create sudoku board display, with separate areas for board and
        # GUI buttons
        centralWidget = QWidget(self)          
        self.setCentralWidget(centralWidget)   
        
        outerLayout = QGridLayout()
        centralWidget.setLayout(outerLayout)
        
        gridLayout = QGridLayout()
        outerLayout.addLayout(gridLayout,0,0,9,9)
        self.CreateBoard(board, candBoard, self, gridLayout)
        
        vLayout = QVBoxLayout()
        outerLayout.addLayout(vLayout,2,9,3,3)
        self.CreateButtons(self, vLayout)
        
        
    def CreateBoard(self, board, candBoard, parent, layout):
        """ Creates board display with initial board values and candidates """
        boxes = [[None for _ in range(3)] for _ in range(3)]
        
        for bi in range(0,3):
            for bj in range(0,3):
                boxes[bi][bj] = Box(parent, board, candBoard, bi, bj)
                layout.addWidget(boxes[bi][bj], bi, bj) 
                
        for i in range(0,9):
            for j in range(0,9):
                candSet = candBoard[i][j]
                bi, bj =  i/3, j/3
                parentBox = boxes[bi][bj]
                self.cells[i][j] = Cell(parentBox, Value2String(board[i][j]), candSet, i, j)
                self.cells[i][j].ConnectCelltoWindow(self.CellClicked)
                parentBox.AddCell(self.cells[i][j], i - 3*bi, j-3*bj)                
                
    def CreateButtons(self, parent, layout):
        """ Create the buttons toolbar for solving options """
        solveButton = QPushButton('Solve')
        solveButton.clicked.connect(lambda: self.Solve())
        layout.addWidget(solveButton)
        
        singleCandButton = QPushButton('Fill Single Candidates')
        singleCandButton.clicked.connect(lambda: self.FillinSingleCandidates())
        layout.addWidget(singleCandButton)

        singleCandStepButton = QPushButton('Fill Single Candidates - Step')
        singleCandStepButton.clicked.connect(lambda: self.FillinSingleCandidatesStep())
        layout.addWidget(singleCandStepButton)
        
        genCandButton = QPushButton('Re-generate Candidates')
        genCandButton.clicked.connect(lambda: self.RegenerateCandidates())
        layout.addWidget(genCandButton)
        
    def CellClicked(self, cell):
        """ Handler function for a cell being clicked.  Makes sure only 1 cell
        is selected at a time ie only 1 cell has focus for input. """
        if self.selectedCell and self.selectedCell is not cell:
            self.selectedCell.Deselect()
   
        self.selectedCell = cell
       
        print ('Clicked on cell ('+str(self.selectedCell.i)+','\
         +str(self.selectedCell.j)+'), with value '+self.selectedCell.cellString)
          
                
    def FillinCell(self, i, j, value):
        """ Will fill in value in a cell if it is empty/unknown """
        
        self.cells[i][j].UpdateValue(Value2String(value))
        
        
    def RemoveCandidatesBasedonCellValue(self, i, j, value):
        """ If have assigned a value to cell i,j remove candidates from block,
        row and column of this cell """

        bi, bj = i/3, j/3
        block = [self.cells[bi*3 + ci][bj*3 + cj] for cj in range(0,3) for ci in range(0,3)]

        for cell in block:
            cell.RemoveCandidate(value)
            
        row_i = self.cells[i]
        for cell in row_i:
            cell.RemoveCandidate(value)

        col_j = [row[j] for row in self.cells]                    
        for cell in col_j:
            cell.RemoveCandidate(value)

    def ResetAllCellsValid(self):
        for i in range(0,9):
            for j in range(0,9):
                self.cells[i][j].SetValidity(isInvalid=False)
    
    def ShowInvalidCells(self, dups):
        self.ResetAllCellsValid()
        for dup in dups:
            self.cells[dup[0]][dup[1]].SetValidity(isInvalid=True)
                
    def UpdateChangedCells(self, prevBoard):
        """ Update the display of changed cells """
        for i in range(0,9):
            for j in range(0,9):
                if prevBoard[i][j] != self.currBoard[i][j]:
                    self.FillinCell(i, j, self.currBoard[i][j])
                    self.RemoveCandidatesBasedonCellValue(i, j, self.currBoard[i][j])
 
    def Solve(self):
        """ Solves the board using the backtracking alogorithm """
        dups = FindDuplicates(self.currBoard)
        if CheckValid(dups):
            prevBoard = deepcopy(self.currBoard)
            
            solved = SolvewBacktrack(self.currBoard)
            
            if not solved:
                print 'No solution'
            else:
                self.UpdateChangedCells(prevBoard)
                
                dups = FindDuplicates(self.currBoard)
                if not CheckValid(dups):
                    print 'Invalid'
                    
        self.ShowInvalidCells(dups)
            
    def FillinSingleCandidatesStep(self):
        """ Look for cells with only 1 candidate and fill them in.
        Updates the candidates after finished """
        dups = FindDuplicates(self.currBoard)
        if CheckValid(dups):
            prevBoard = deepcopy(self.currBoard)
            
            changed, self.currBoard, self.candBoard = FillSingleCandidates(self.currBoard, self.candBoard)
            if changed:
                self.UpdateChangedCells(prevBoard)
            
            dups = FindDuplicates(self.currBoard)
            if not CheckValid(dups):
                print 'Invalid'
                
        self.ShowInvalidCells(dups)

        
    def FillinSingleCandidates(self):
        """ Look for cells with only 1 candidate and fill them in 
        Then update candidates and iterate until no more changes """
        dups = FindDuplicates(self.currBoard)
        if CheckValid(dups):
            notdone = True
            
            prevBoard = deepcopy(self.currBoard)
            
            while notdone:
                notdone, self.currBoard, self.candBoard = FillSingleCandidates(self.currBoard, self.candBoard)
    
            self.UpdateChangedCells(prevBoard)
                        
            dups = FindDuplicates(self.currBoard)
            if not CheckValid(dups):
                print 'Invalid'
                
        self.ShowInvalidCells(dups)
        
    def RegenerateCandidates(self):
        self.candBoard = SolveCandidates(self.currBoard)
        
        for i in range(0,9):
            for j in range(0,9):
                candSet = self.candBoard[i][j]     
                self.cells[i][j].UpdateCandidates(candSet)
                
    def mouseReleaseEvent(self, QMouseEvent):
        """ If mouse clicked not on child widget such as a cell """
        if self.selectedCell:
            self.selectedCell.Deselect()
        self.selectedCell = None
        print('('+str(QMouseEvent.x())+', '+str(QMouseEvent.y())+') \
              ('+str(self.width())+','+str(self.height())+')')
        
    def keyPressEvent(self, event):
        """ Handles key presses.  If is a number key, update the value in selected
        cell  """
        key = event.key()
        keyStr = event.text()
        
        if self.selectedCell and self.selectedCell.CanEdit():
        
            # If number key pressed
            if QtCore.Qt.Key_1 <= key <= QtCore.Qt.Key_9:                    
                self.selectedCell.UpdateValue(keyStr)
                self.currBoard[self.selectedCell.i][self.selectedCell.j] = int(keyStr)
                self.candBoard = SolveCandidates(self.currBoard)
                    
            if key == QtCore.Qt.Key_Backspace:
                self.selectedCell.UpdateValue(' ')
                self.currBoard[self.selectedCell.i][self.selectedCell.j] = 0
                self.candBoard = SolveCandidates(self.currBoard)
            
            dups = FindDuplicates(self.currBoard)
            if not CheckValid(dups):
                print 'Invalid'
                print dups
            
            self.ShowInvalidCells(dups)
                

###############################################################################
# Main App function - creates the app and window then passes control to the 
# app GUI.  Returns when app quits

def run_app(origBoard):
    """ Main application function """
    print 'Board is valid:', CheckValid(FindDuplicates(origBoard))
    
    candBoard = SolveCandidates(origBoard)

    app = QtWidgets.QApplication(sys.argv)
    mainWin = SudokuMainWindow(origBoard, candBoard)
    mainWin.show()
    
    return app.exec_()


###############################################################################

def UnitTests():
    print '######### Unit Tests #############'
    testboard = [
    [7,8,0,4,0,0,1,2,0],
    [6,0,0,0,7,5,0,0,9],
    [0,0,0,6,0,1,0,7,8],
    [0,0,7,0,4,0,2,6,0],
    [0,0,1,0,5,0,9,3,0],
    [9,0,4,0,6,0,0,0,5],
    [0,7,0,3,0,0,0,1,2],
    [1,2,0,0,0,7,4,0,0],
    [0,4,9,2,0,6,0,0,7]
    ]
    
    testboard[4][4] = 3    
    print 'Check valid via Row Duplicate Test. Should be False', CheckValid(FindDuplicates(testboard))
    
    testboard[4][4] = 7
    print 'Check valid via Col Duplicate Test. Should be False', CheckValid(FindDuplicates(testboard))
    
    testboard[4][4] = 5
    testboard[8][8] = 1
    print 'Check valid via Block Duplicate Test. Should be False', CheckValid(FindDuplicates(testboard))
    
    print '######### End Unit Tests #############'

###############################################################################
                
if __name__ == "__main__":  
    
    UnitTests()
    
    easyboard = [
    [0,8,0,0,0,0,3,5,0],
    [5,0,4,0,8,0,1,9,0],
    [0,3,0,0,4,0,0,2,8],
    [0,0,0,0,0,9,6,0,0],
    [0,6,3,0,0,0,4,0,2],
    [0,0,0,7,0,0,0,1,3],
    [4,2,0,3,9,0,0,0,7],
    [3,5,6,0,0,8,0,4,0],
    [0,0,8,0,2,4,5,0,0]
    ]

    hardboard = [
    [0,0,0,0,0,0,4,0,0],
    [0,0,1,0,7,0,0,9,0],
    [5,0,0,0,3,0,0,0,6],
    [0,8,0,2,0,0,0,0,0],
    [7,0,0,0,0,0,9,2,0],
    [1,2,0,6,0,5,0,0,0],
    [0,5,0,0,0,0,0,4,0],
    [0,7,3,9,0,8,0,0,0],
    [6,0,0,4,5,0,2,0,0]
    ]    
    sys.exit(run_app(easyboard))