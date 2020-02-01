import sys
from copy import deepcopy
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget
#from PyQt5.QtCore import QSize    

from PyQt5.QtGui import QFont#, QPainter, QBrush, QPen, QCursor

from os import environ

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    
environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

def Value2String(value):
    return str(value) if value is not 0 else ' '
    
class Cell(QLabel):
    def __init__(self, parent, strValue, i, j):
        super(QLabel, self).__init__(strValue, parent)
        self.cellString = strValue
        
        self.setStyleSheet("background-color: white;")
        self.setAlignment(QtCore.Qt.AlignCenter)
        cellfont = QFont("Arial", 45, QFont.Bold) 
        candidatefont = QFont("Arial", 12)

        self.setFont(cellfont)
        self.i = i
        self.j = j
        
        if strValue == ' ':
            gridLayoutBox = QGridLayout() 
            self.setLayout(gridLayoutBox) 
            for i in range(0,3):
                for j in range(0,3):
                    candValue = str(3*i + j + 1)
                    candLabel = QLabel(candValue, self)
                    candLabel.setFont(candidatefont)
                    gridLayoutBox.addWidget(candLabel, i, j)            
        
    def mouseReleaseEvent(self, QMouseEvent):
        print ('Clicked on cell ('+str(self.i)+','+str(self.j)+'), with value '+self.cellString)
        
class Box(QLabel):
    def __init__(self, parent, bi, bj):
        super(QLabel, self).__init__(parent)
        self.setStyleSheet("background-color: lightgrey;")
        self.bi = bi
        self.bj = bj
                
        gridLayoutBox = QGridLayout() 
        self.setLayout(gridLayoutBox) 
        
        for i in range(0,3):
            for j in range(0,3):
                ci = bi*3 + i
                cj = bj*3 + j
                strValue = Value2String(board[ci][cj])
                cellLabel = Cell(self, strValue, ci, cj)
                gridLayoutBox.addWidget(cellLabel, i, j) 
     
class SudokuMainWindow(QMainWindow):
    def __init__(self, board):
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
        
        self.CreateBoard(board, self, gridLayout)
        
    def CreateBoard(self, board, parent, layout):
        for bi in range(0,3):
            for bj in range(0,3):
                box = Box(parent, bi, bj)
                layout.addWidget(box, bi, bj)  
        
    def mouseReleaseEvent(self, QMouseEvent):
        print('('+str(QMouseEvent.x())+', '+str(QMouseEvent.y())+') \
              ('+str(self.width())+','+str(self.height())+')')
        
def run_app(board): 
    app = QtWidgets.QApplication(sys.argv)
    mainWin = SudokuMainWindow(board)
    mainWin.show()
    return app.exec_()

###############################################################################

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
                
if __name__ == "__main__":  
    board = [
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
    
    
    
    boardwCands = SolveCandidates(board)
    
    print boardwCands
    
    sys.exit(run_app(board))