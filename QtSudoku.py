import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget
from PyQt5.QtCore import QSize    

from PyQt5.QtGui import QPainter, QBrush, QPen


     
class SudokuMainWindow(QMainWindow):
    def __init__(self, board):
        super(QMainWindow, self).__init__()
 
        self.setMinimumSize(QSize(100, 100))    
        self.setWindowTitle("Simple Sudoku") 
        
        centralWidget = QWidget(self)          
        self.setCentralWidget(centralWidget)   
 
        gridLayout = QGridLayout()     
        centralWidget.setLayout(gridLayout)  
        
        self.CreateBoard(board, gridLayout)
       
        menu = self.menuBar().addMenu('File')
        action = menu.addAction('Quit')
        action.triggered.connect(QtWidgets.QApplication.quit)
        
    def CreateBoard(self, board, gridLayout):
        for i in range(0,9):
            for j in range(0,9):
                cellString = str(board[i][j]) if board[i][j] is not 0 else ' '
                cellLabel = QLabel(cellString, self) 
                cellLabel.setAlignment(QtCore.Qt.AlignCenter)
                gridLayout.addWidget(cellLabel, i, j) 
                
if __name__ == "__main__":
    def run_app():
        
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
        
        app = QtWidgets.QApplication(sys.argv)
        mainWin = SudokuMainWindow(board)
        mainWin.show()
        return app.exec_()

    sys.exit(run_app())