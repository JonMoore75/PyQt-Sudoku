import sys
from copy import deepcopy
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
Signal, Slot = pyqtSignal, pyqtSlot 
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, \
    QPushButton, QHBoxLayout, QVBoxLayout    

from PyQt5.QtGui import QFont

from os import environ

import Sudoku as sd

###############################################################################

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    
environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"


    
###############################################################################
# View - this is the pyQT5 GUI dealing with input and display

def Value2String(value):
    return str(value) if value is not 0 else ' '
        
#####################     
    
class Candidate(QLabel):
    def __init__(self, strValue, parent):
        super(QLabel, self).__init__(strValue, parent)
        self.setStyleSheet("""
           Candidate[hilite="true"] {color: orange;}
           Candidate[hilite="false"] {color: black;}
            """)
        
        self.SetHilite(False)
        
        self.setFont(QFont("Arial", 12))
        self.setAttribute(Qt.WA_TranslucentBackground)

        
    def SetHilite(self, isHilited):
        """ Set or remove highlight for this candidate """
        self.setProperty('hilite', isHilited)
        self.style().unpolish(self)
        self.style().polish(self)
        
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

        self.setFont(QFont("Arial", 45, QFont.Bold))
        
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
                candLabel = Candidate(candStr, self)
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
                    candWidget = self.gridLayoutBox.itemAtPosition(i, j).widget()
                    candWidget.setText(candStr)
                    
    def HiliteCandidates(self, candSet):
        """ Highlight candidates in this cell given by candSet """
        if self.cellString == ' ':           
            for cand in iter(candSet):
                i, j = (cand-1)/3, (cand-1)%3
                candWidget = self.gridLayoutBox.itemAtPosition(i, j).widget()
                candWidget.SetHilite(True)   
                
    def ClearHilites(self):
        pass
        if self.cellString == ' ':           
            for cand in range(1,10):
                i, j = (cand-1)/3, (cand-1)%3
                candWidget = self.gridLayoutBox.itemAtPosition(i, j).widget()
                candWidget.SetHilite(False) 
                
    def RemoveCandidate(self, value):
        """ Removes candidate value from empty/unknown cell """
        if self.cellString == ' ': 
            i, j = (value-1)/3, (value-1) % 3
            candWidget = self.gridLayoutBox.itemAtPosition(i, j).widget()
            candWidget.setText(' ')
                    
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
        
#        singleCandButton = QPushButton('Fill Single Candidates')
#        singleCandButton.clicked.connect(lambda: self.FillinSingleCandidates())
#        layout.addWidget(singleCandButton)

        singleCandStepButton = QPushButton('Fill Single Candidates - Step')
        singleCandStepButton.clicked.connect(lambda: self.FillinSingleCandidatesStep())
        layout.addWidget(singleCandStepButton)
        
        genCandButton = QPushButton('Re-generate Candidates')
        genCandButton.clicked.connect(lambda: self.RegenerateCandidates())
        layout.addWidget(genCandButton)
        
        hiddenSingleButton = QPushButton('Highlight Hidden Singles')
        hiddenSingleButton.clicked.connect(lambda: self.HighlightHiddenSingles())
        layout.addWidget(hiddenSingleButton)
        
        nakedPairButton = QPushButton('Highlight Naked Pairs')
        nakedPairButton.clicked.connect(lambda: self.HighlightNakedPairs())
        layout.addWidget(nakedPairButton) 
        
        pointPairButton = QPushButton('Highlight Pointing Pairs')
        pointPairButton.clicked.connect(lambda: self.HighlightPointingPairs())
        layout.addWidget(pointPairButton)
        
        boxlinePairButton = QPushButton('Highlight Box-Line Pairs')
        boxlinePairButton.clicked.connect(lambda: self.HighlightBoxLinePairs())
        layout.addWidget(boxlinePairButton)
        
        clearHiliteButton = QPushButton('Clear Highlights')
        clearHiliteButton.clicked.connect(lambda: self.ClearHighlights())
        layout.addWidget(clearHiliteButton)
                
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
        """ Remove indication of invalid cells """
        for i in range(0,9):
            for j in range(0,9):
                self.cells[i][j].SetValidity(isInvalid=False)
    
    def ShowInvalidCells(self, dups):
        """ Highlight cells that are a duplicate of that number in row, column 
        or block.  List of duplicates passed in as list of tuple (i,j) pairs. """
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
        dups = sd.FindDuplicates(self.currBoard)
        if sd.CheckValid(dups):
            prevBoard = deepcopy(self.currBoard)
            
            solved = sd.SolvewBacktrack(self.currBoard)
            
            if not solved:
                print 'No solution'
            else:
                self.UpdateChangedCells(prevBoard)
                
                dups = sd.FindDuplicates(self.currBoard)
                if not sd.CheckValid(dups):
                    print 'Invalid'
                    
        self.ShowInvalidCells(dups)
            
    def FillinSingleCandidatesStep(self):
        """ Look for cells with only 1 candidate and fill them in.
        Updates the candidates after finished """
        dups = sd.FindDuplicates(self.currBoard)
        if sd.CheckValid(dups):
            prevBoard = deepcopy(self.currBoard)
            
            changed, self.currBoard, self.candBoard = sd.FillSingleCandidates(self.currBoard, self.candBoard)
            if changed:
                self.UpdateChangedCells(prevBoard)
            
            dups = sd.FindDuplicates(self.currBoard)
            if not sd.CheckValid(dups):
                print 'Invalid'
                
        self.ShowInvalidCells(dups)

        
    def FillinSingleCandidates(self):
        """ Look for cells with only 1 candidate and fill them in 
        Then update candidates and iterate until no more changes """
        dups = sd.FindDuplicates(self.currBoard)
        if sd.CheckValid(dups):
            notdone = True
            
            prevBoard = deepcopy(self.currBoard)
            
            while notdone:
                notdone, self.currBoard, self.candBoard = sd.FillSingleCandidates(self.currBoard, self.candBoard)
    
            self.UpdateChangedCells(prevBoard)
                        
            dups = sd.FindDuplicates(self.currBoard)
            if not sd.CheckValid(dups):
                print 'Invalid'
                
        self.ShowInvalidCells(dups)
        
    def ClearHighlights(self):
        for i in range(0,9):
            for j in range(0,9):
                self.cells[i][j].ClearHilites()
        
    def HighlightHiddenSingles(self):
        self.ClearHighlights()
        hiddenSingles = sd.HiddenSingles(self.currBoard, self.candBoard)
                
        for hiddenSingle in hiddenSingles:
            i,j,n = hiddenSingle
            self.cells[i][j].HiliteCandidates(set([n]))
            
    def HighlightNakedPairs(self):
        self.ClearHighlights()
        pairSets = sd.NakedPairs(self.currBoard, self.candBoard)
        
        for pairSet in pairSets:
            a,b,i1,j1,i2,j2 = pairSet
            self.cells[i1][j1].HiliteCandidates(set([a,b]))
            self.cells[i2][j2].HiliteCandidates(set([a,b]))
            
    def HighlightPointingPairs(self):
        self.ClearHighlights()
        
        pairSets = sd.PointingPairs(self.currBoard, self.candBoard)
        
        for pairSet in pairSets:
            n,i1,j1,i2,j2 = pairSet
            self.cells[i1][j1].HiliteCandidates(set([n]))
            self.cells[i2][j2].HiliteCandidates(set([n]))
            
    def HighlightBoxLinePairs(self):
        self.ClearHighlights()
        pairSets = sd.BoxLinePairs(self.currBoard, self.candBoard)
        
        for pairSet in pairSets:
            n,i1,j1,i2,j2 = pairSet
            self.cells[i1][j1].HiliteCandidates(set([n]))
            self.cells[i2][j2].HiliteCandidates(set([n]))
        
    def RegenerateCandidates(self):
        """ Reset the displayed candidates to those based on those that are 
        valid (ie avoid duplicates)"""
        self.candBoard = sd.SolveCandidates(self.currBoard)
        
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
                self.candBoard = sd.SolveCandidates(self.currBoard)
                    
            if key == QtCore.Qt.Key_Backspace:
                self.selectedCell.UpdateValue(' ')
                self.currBoard[self.selectedCell.i][self.selectedCell.j] = 0
                self.candBoard = sd.SolveCandidates(self.currBoard)
            
            dups = sd.FindDuplicates(self.currBoard)
            if not sd.CheckValid(dups):
                print 'Invalid', dups
            
            self.ShowInvalidCells(dups)
                

###############################################################################
# Main App function - creates the app and window then passes control to the 
# app GUI.  Returns when app quits

def run_app(origBoard):
    """ Main application function """
    print 'Board is valid:', sd.CheckValid(sd.FindDuplicates(origBoard))
    
    candBoard = sd.SolveCandidates(origBoard)

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
    print 'Check valid via Row Duplicate Test. Should be False', \
        sd.CheckValid(sd.FindDuplicates(testboard))
    
    testboard[4][4] = 7
    print 'Check valid via Col Duplicate Test. Should be False', \
        sd.CheckValid(sd.FindDuplicates(testboard))
    
    testboard[4][4] = 5
    testboard[8][8] = 1
    print 'Check valid via Block Duplicate Test. Should be False', \
        sd.CheckValid(sd.FindDuplicates(testboard))
    
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
    
    obsboard=[
    [0,7,0,0,0,0,9,1,6],
    [4,5,1,3,6,9,7,8,2],
    [0,6,9,0,0,1,3,5,4],
    [0,0,7,0,0,6,1,0,8],
    [0,0,8,0,0,0,6,0,0],
    [6,0,0,1,9,8,0,0,0],
    [0,0,6,9,0,0,8,0,0],
    [7,8,0,6,1,2,0,3,9],
    [9,3,0,4,8,7,0,6,1],
    ]
    sys.exit(run_app(hardboard))