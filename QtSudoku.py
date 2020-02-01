import sys
from copy import deepcopy
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget
#from PyQt5.QtCore import QSize    

from PyQt5.QtGui import QFont#, QPainter, QBrush, QPen, QCursor

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

def SolveCandidates(board):
    """ Takes a Sudoku board (2d 9x9 list of ints with 0 as empty cell) and 
    returns a board that is a 2d 9x9 list of sets.  Each set is the possible 
    int values. Known values are now sets with 1 item. """
    boardcopy = deepcopy(board)
    for i in range(0,9):
        for j in range(0,9):
            if board[i][j] == 0:
                boardcopy[i][j] = GetCandidateList(board, i, j)
            else:
                boardcopy[i][j] = set([board[i][j]])
    return boardcopy

###############################################################################

def Value2String(value):
    return str(value) if value is not 0 else ' '
    
class Cell(QLabel):
    def __init__(self, parent, strValue, candSet, i, j):
        super(QLabel, self).__init__(strValue, parent)
        self.cellString = strValue
        
        self.setStyleSheet("background-color: white;")
        self.setAlignment(QtCore.Qt.AlignCenter)
        cellfont = QFont("Arial", 45, QFont.Bold) 
        candidatefont = QFont("Arial", 12)

        self.setFont(cellfont)
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
                    candLabel.setFont(candidatefont)
                    self.gridLayoutBox.addWidget(candLabel, i, j)
                    
    def UpdateValue(self, strValue):
        """ Will fill in value in a cell if it is empty/unknown """
        if self.cellString == ' ' and strValue != ' ':
            # Delete all candidate label widgets 
            for i in reversed(range(self.gridLayoutBox.count())): 
                self.gridLayoutBox.itemAt(i).widget().setParent(None)
                
            self.setText(strValue)
            self.cellString = strValue
            self.setStyleSheet('background-color: white; color: darkgrey')
            self.update()
        
        
    def mouseReleaseEvent(self, QMouseEvent):
        """ Prints the cell clicked on """
        print ('Clicked on cell ('+str(self.i)+','+str(self.j)+'), with value '+self.cellString)
        
class Box(QLabel):
    def __init__(self, parent, board, candBoard, bi, bj):
        super(QLabel, self).__init__(parent)
        self.setStyleSheet("background-color: lightgrey;")
        self.bi = bi
        self.bj = bj
                
        self.gridLayoutBox = QGridLayout() 
        self.setLayout(self.gridLayoutBox) 
        
        for i in range(0,3):
            for j in range(0,3):
                ci = bi*3 + i
                cj = bj*3 + j
                strValue = Value2String(board[ci][cj])
                candSet = candBoard[ci][cj]
                cellLabel = Cell(self, strValue, candSet, ci, cj)
                self.gridLayoutBox.addWidget(cellLabel, i, j)
                
    def FillinCell(self, i, j, value):
        """ Will fill in value in a cell if it is empty/unknown """
        ci = i - 3*self.bi
        cj = j - 3*self.bj
        
        cell = self.gridLayoutBox.itemAtPosition(ci, cj).widget()
        cell.UpdateValue(Value2String(value))
     
class SudokuMainWindow(QMainWindow):
    def __init__(self, board, candBoard):
        super(QMainWindow, self).__init__()
 
        self.setGeometry(500, 30, 900, 900)    
        self.setWindowTitle("Simple Sudoku") 
        self.setStyleSheet("background-color: grey;")
        
        centralWidget = QWidget(self)          
        self.setCentralWidget(centralWidget)   
 
        gridLayout = QGridLayout()     
#        gridLayout.setVerticalSpacing(2)
#        gridLayout.setHorizontalSpacing(2)
        centralWidget.setLayout(gridLayout)  
        
        self.CreateBoard(board, candBoard, self, gridLayout)
        
    def CreateBoard(self, board, candBoard, parent, layout):
        """ Creates board display with initial board values and candidates """
        self.boxes = [[None for _ in range(3)] for _ in range(3)]
        for bi in range(0,3):
            for bj in range(0,3):
                self.boxes[bi][bj] = Box(parent, board, candBoard, bi, bj)
                layout.addWidget(self.boxes[bi][bj], bi, bj)  
                
    def FillinCell(self, i, j, value):
        """ Will fill in value in a cell if it is empty/unknown """
        bi = i/3
        bj = j/3
        
        self.boxes[bi][bj].FillinCell(i, j, value)
        
    def FillinSingleCandidates(self, board, candBoard):
        """ Look for cells with only 1 candidate and fill them in 
        Then update candidates and iterate.  Each change check validity.  
        If not valid then break out to prevent loops. """
        changes = False
        for i in range(0,9):
            for j in range(0,9): 
                if len(candBoard[i][j]) == 1 and board[i][j] == 0:
                    changes = True
                    board[i][j] = next(iter(candBoard[i][j]))
                    self.FillinCell(i, j, board[i][j])
                    
                    candBoard = SolveCandidates(board)
                    
                    if not CheckValid(board):
                        return
        
        if changes:
            self.FillinSingleCandidates(board, candBoard)
        
    def mouseReleaseEvent(self, QMouseEvent):
        print('('+str(QMouseEvent.x())+', '+str(QMouseEvent.y())+') \
              ('+str(self.width())+','+str(self.height())+')')
###############################################################################


def run_app(origBoard):
    print 'Board is valid:', CheckValid(origBoard)
    
    candBoard = SolveCandidates(origBoard)

    app = QtWidgets.QApplication(sys.argv)
    mainWin = SudokuMainWindow(origBoard, candBoard)
    mainWin.show()
    
    currBoard = deepcopy(origBoard)
    
    mainWin.FillinSingleCandidates(currBoard, candBoard)
    
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
    boardcopy = deepcopy(testboard)
    
    boardcopy[4][4] = 3    
    print 'Check valid via Row Duplicate Test. Should be False', CheckValid(boardcopy)
    
    boardcopy[4][4] = 7
    print 'Check valid via Col Duplicate Test. Should be False', CheckValid(boardcopy)
    
    boardcopy[4][4] = 5
    boardcopy[8][8] = 1
    print 'Check valid via Block Duplicate Test. Should be False', CheckValid(boardcopy)
    
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