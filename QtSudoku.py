import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget
from PyQt5.QtCore import QSize    

from PyQt5.QtGui import QPainter, QBrush, QPen, QCursor, QFont

class Cell(QLabel):
    def __init__(self, value, font, parent):
        self.cellString = str(value) if value is not 0 else ' '
        super(QLabel, self).__init__(self.cellString, parent)
        self.setStyleSheet("background-color: white;")
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFont(font)
        
    def mouseReleaseEvent(self, QMouseEvent):
        print 'Clicked on '+self.cellString
     
class SudokuMainWindow(QMainWindow):
    def __init__(self, board):
        super(QMainWindow, self).__init__()
 
        self.setFixedSize(QSize(500, 500))    
        self.setWindowTitle("Simple Sudoku") 
        self.setStyleSheet("background-color: grey;")
        
        centralWidget = QWidget(self)          
        self.setCentralWidget(centralWidget)   
 
        gridLayout = QGridLayout()     
        centralWidget.setLayout(gridLayout)  
        
        self.CreateBoard(board, gridLayout)
       
#        menu = self.menuBar().addMenu('File')
#        action = menu.addAction('Quit')
#        action.triggered.connect(QtWidgets.QApplication.quit)
        
    def CreateBoard(self, board, gridLayout):
        cellfont = QFont("Arial", 25, QFont.Bold) 
        for i in range(0,9):
            for j in range(0,9):
                cellLabel = Cell(board[i][j], cellfont, self)
                gridLayout.addWidget(cellLabel, i, j) 
        
    def mouseReleaseEvent(self, QMouseEvent):
        my = self.menuBar().height()
        print('('+str(QMouseEvent.x())+', '+str(QMouseEvent.y()-my)+') \
              ('+str(self.width())+','+str(self.height())+')')

                
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