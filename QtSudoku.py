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
def checkListForDuplicates(listOfElems):
    """ Check if given list contains any duplicates """
    if len(listOfElems) == len(set(listOfElems)):
        return False
    else:
        return True
    
def CheckValid(board):
    """ Check if no duplicate entries on any row, column or block """
    for i in range(0,9):
        row_i = board[i]
        if checkListForDuplicates(RemoveZeros(row_i)):
            return False
        
    for j in range(0,9):
        col_j = [row[j] for row in board]
        if checkListForDuplicates(RemoveZeros(col_j)):
            return False
        
    for bi in range(0,3):
        for bj in range(0,3):
            block = [[board[bi*3 + ci][bj*3 + cj] for cj in range(0,3)] for ci in range(0,3)]
            if checkListForDuplicates(RemoveZeros([c for row in block for c in row])):
                return False
            
    return True

def RemoveZeros(inputList):
    """ Remove zeros from a list """
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

def Value2String(value):
    return str(value) if value is not 0 else ' '
        
#####################      
  
class Cell(QLabel):
    selected = Signal(object)
    def __init__(self, parent, strValue, candSet, i, j):
        super(QLabel, self).__init__(strValue, parent)
        self.cellString = strValue

        self.setStyleSheet("""
           Cell[selected="true"] {background-color: lightblue;}
           Cell[selected="false"] {background-color: white;}
           Cell[edit="true"] {color: darkgrey;}
           Cell[edit="false"] {color: black;}
            """)
        self.setProperty('selected', False)
        self.setProperty('edit', False)
        self.style().unpolish(self)
        self.style().polish(self)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.cellfont = QFont("Arial", 45, QFont.Bold) 
        self.candidatefont = QFont("Arial", 12)

        self.setFont(self.cellfont)
        self.i = i
        self.j = j
        
        if self.cellString == ' ':
            self.gridLayoutBox = QGridLayout() 
            self.setLayout(self.gridLayoutBox) 
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
                    
    def UpdateValue(self, strValue):
        """ Will fill in value in a cell if it is empty/unknown """
        if self.cellString == ' ' and strValue != ' ':
            # Delete all candidate label widgets 
            for i in reversed(range(self.gridLayoutBox.count())): 
                self.gridLayoutBox.itemAt(i).widget().setParent(None)
                
            self.setText(strValue)
            self.cellString = strValue
            
            self.setProperty('edit', True)
            self.style().unpolish(self)
            self.style().polish(self)

            
    def UpdateCandidates(self, candSet):
        """ Updates the valid candidates for empty/unknown cell """
        if self.cellString == ' ': 
            for i in range(0,3):
                for j in range(0,3):
                    candValue = 3*i + j + 1
                    candStr = str(candValue) if candValue in candSet else ' '
                    cand = self.gridLayoutBox.itemAtPosition(i, j).widget()
                    cand.setText(candStr)
                    
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
        self.bi = bi
        self.bj = bj
                
        self.gridLayoutBox = QGridLayout() 
        self.setLayout(self.gridLayoutBox) 
        
        # Setup the 9 child cells in this box
        for i in range(0,3):
            for j in range(0,3):
                ci = bi*3 + i
                cj = bj*3 + j
                strValue = Value2String(board[ci][cj])
                candSet = candBoard[ci][cj]
                cellLabel = Cell(self, strValue, candSet, ci, cj)
                self.gridLayoutBox.addWidget(cellLabel, i, j)
                
    def UpdateCandidates(self, i, j, candSet):
        """ Updates the valid candidates for empty/unknown cell """
        ci = i - 3*self.bi
        cj = j - 3*self.bj
        
        cell = self.gridLayoutBox.itemAtPosition(ci, cj).widget()
        cell.UpdateCandidates(candSet)
        
    def GetCell(self, i,j):
        """ Return the cell at coords i,j in the board """
        ci = i - 3*self.bi
        cj = j - 3*self.bj
        if ci > 2 or cj >2 or ci < 0 or cj < 0:
            raise ValueError('Asking for cell not in this box')
        return self.gridLayoutBox.itemAtPosition(ci, cj).widget()
                
    def FillinCell(self, i, j, value):
        """ Will fill in value in a cell if it is empty/unknown.
        Assumes this is correct box """        
        cell = self.GetCell(i,j)
        cell.UpdateValue(Value2String(value))
        
    def ConnectCellstoWindow(self, ClickFunc):
        """ Pass handler function for cell being clicked to each cell """
        for i in range(0,3):
            for j in range(0,3):
                cell = self.gridLayoutBox.itemAtPosition(i, j).widget()
                cell.ConnectCelltoWindow(ClickFunc)
        
#####################      
     
class SudokuMainWindow(QMainWindow):
    def __init__(self, board, candBoard):
        super(QMainWindow, self).__init__()
        
        self.currBoard = deepcopy(board)
        self.candBoard = deepcopy(candBoard)
 
        self.setGeometry(500, 30, 1200, 900)    
        self.setWindowTitle("Simple Sudoku") 
        self.setStyleSheet("background-color: grey;")
        
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
        
        self.selectedCell = None
        
    def CreateBoard(self, board, candBoard, parent, layout):
        """ Creates board display with initial board values and candidates """
        self.boxes = [[None for _ in range(3)] for _ in range(3)]
        for bi in range(0,3):
            for bj in range(0,3):
                self.boxes[bi][bj] = Box(parent, board, candBoard, bi, bj)
                self.boxes[bi][bj].ConnectCellstoWindow(self.CellClicked)
                layout.addWidget(self.boxes[bi][bj], bi, bj)  
                
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
        bi = i/3
        bj = j/3
        
        self.boxes[bi][bj].FillinCell(i, j, value)
        
    def UpdateChangedCells(self, prevBoard, prevCandBoard):
        """ Update the display of changed cells """
        for i in range(0,9):
            for j in range(0,9):
                if prevBoard[i][j] != self.currBoard[i][j]:
                    self.FillinCell(i, j, self.currBoard[i][j])
                if len(prevCandBoard[i][j]) != len(self.candBoard[i][j]):
                    candSet = self.candBoard[i][j]
                    bi = i/3
                    bj = j/3
                    self.boxes[bi][bj].UpdateCandidates(i, j, candSet)
 
    def Solve(self):
        """ Placeholder for backtracking solver """
        prevBoard = deepcopy(self.currBoard)
        
        solved = SolvewBacktrack(self.currBoard)
        
        if not solved:
            print 'No solution'
        
        self.UpdateChangedCells(prevBoard, self.candBoard)
        if not CheckValid(self.currBoard):
            print 'Invalid'
            
    def FillinSingleCandidatesStep(self):
        """ Look for cells with only 1 candidate and fill them in.
        Updates the candidates after finished """
        
        prevBoard = deepcopy(self.currBoard)
        prevCandBoard = deepcopy(self.candBoard)
        
        changed, self.currBoard, self.candBoard = FillSingleCandidates(self.currBoard, self.candBoard)
        self.UpdateChangedCells(prevBoard, prevCandBoard)
        
        if not CheckValid(self.currBoard):
            print 'Invalid'

        
    def FillinSingleCandidates(self):
        """ Look for cells with only 1 candidate and fill them in 
        Then update candidates and iterate until no more changes """
        
        notdone = True
        
        prevBoard = deepcopy(self.currBoard)
        prevCandBoard = deepcopy(self.candBoard)
        
        while notdone:
            notdone, self.currBoard, self.candBoard = FillSingleCandidates(self.currBoard, self.candBoard)

        self.UpdateChangedCells(prevBoard, prevCandBoard)
                    
        if not CheckValid(self.currBoard):
            print 'Invalid'
        
    def mouseReleaseEvent(self, QMouseEvent):
        """ If mouse clicked not on child widget """
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
         
        if QtCore.Qt.Key_1 <= key <= QtCore.Qt.Key_9 and self.selectedCell:
            self.selectedCell.UpdateValue(keyStr)
            self.currBoard[self.selectedCell.i][self.selectedCell.j] = int(keyStr)
    

###############################################################################


def run_app(origBoard):
    """ Main application function """
    print 'Board is valid:', CheckValid(origBoard)
    
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
    print 'Check valid via Row Duplicate Test. Should be False', CheckValid(testboard)
    
    testboard[4][4] = 7
    print 'Check valid via Col Duplicate Test. Should be False', CheckValid(testboard)
    
    testboard[4][4] = 5
    testboard[8][8] = 1
    print 'Check valid via Block Duplicate Test. Should be False', CheckValid(testboard)
    
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
    sys.exit(run_app(hardboard))