import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget
from PyQt5.QtCore import QSize    

from PyQt5.QtGui import QPainter, QBrush, QPen
     
class SudokuMainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
 
        self.setMinimumSize(QSize(100, 100))    
        self.setWindowTitle("Simple Sudoku") 
        
        centralWidget = QWidget(self)          
        self.setCentralWidget(centralWidget)   
 
        gridLayout = QGridLayout(self)     
        centralWidget.setLayout(gridLayout)  
        
        for i in range(0,9):
            for j in range(0,9):
                title = QLabel(str(j+1), self) 
                title.setAlignment(QtCore.Qt.AlignCenter)
                gridLayout.addWidget(title, i, j)
       
        menu = self.menuBar().addMenu('File')
        action = menu.addAction('Quit')
        action.triggered.connect(QtWidgets.QApplication.quit)
 
if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        mainWin = SudokuMainWindow()
        mainWin.show()
        return app.exec_()

    sys.exit(run_app())