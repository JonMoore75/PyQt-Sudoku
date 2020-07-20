import sys
from copy import deepcopy
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot
Signal, Slot = pyqtSignal, pyqtSlot 
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, \
    QPushButton, QHBoxLayout, QVBoxLayout

from PyQt5.QtGui import QFont

from os import environ

import Sudoku as sd

###############################################################################
# Allow HighDPI Scaling

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    
environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
###############################################################################


def Value2String(value):
    return str(value) if value is not 0 else ' '
        
#####################     
    
class Candidate(QLabel):
    def __init__(self, strValue, parent):
        super(QLabel, self).__init__(strValue, parent)
        self.setStyleSheet("""
           Candidate[hilite="red"] {background-color: red;}
           Candidate[hilite="green"] {background-color: lightgreen;}
           Candidate[hilite="off"] {background: transparent;}
            """)
        
        self.SetHilite('off')
        
        self.setFont(QFont("Arial", 12))
        self.setAlignment(QtCore.Qt.AlignCenter)
#        self.setAttribute(Qt.WA_TranslucentBackground)

        
    def SetHilite(self, hiliteColour='off'):
        """ Set or remove highlight for this candidate """
        self.setProperty('hilite', hiliteColour)
        self.style().unpolish(self)
        self.style().polish(self)
        
#####################
        
class Cell(QLabel):
    selected = Signal(object, int)
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
        """ Specifies the function to pass events to when this cell is clicked on by the 
        mouse """ 
        self.selected.connect(ClickFunc)
        
    def CanEdit(self):
        return self.property('edit')
        
    def SetValidity(self, isInvalid):
        """ If the value in this cell conflicts with the value in another cell
        then highlight it """
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
                    
    def HiliteCandidates(self, candSet, colour='green'):
        """ Highlight candidates in this cell given by candSet """
        if self.cellString == ' ':           
            for cand in iter(candSet):
                i, j = (cand-1)//3, (cand-1)%3
                candWidget = self.gridLayoutBox.itemAtPosition(i, j).widget()
                candWidget.SetHilite(colour)   
                
    def ClearHilites(self):
        """ Remove any candidate highlighting from this cell """
        if self.cellString == ' ':           
            for cand in range(1,10):
                i, j = (cand-1)//3, (cand-1)%3
                candWidget = self.gridLayoutBox.itemAtPosition(i, j).widget()
                candWidget.SetHilite('off') 
                
    def RemoveCandidate(self, value):
        """ Removes candidate value from empty/unknown cell """
        if self.cellString == ' ': 
            i, j = (value-1)//3, (value-1) % 3
            candWidget = self.gridLayoutBox.itemAtPosition(i, j).widget()
            candWidget.setText(' ')
                    
    def ToggleCandidateClicked(self): 
        """ Toggles the candidate number if under the mouse """                   
        for i in range(0,3):
            for j in range(0,3):
                candValue = 3*i + j + 1
                cand = self.gridLayoutBox.itemAtPosition(i, j).widget()
                if cand.underMouse():
                    candStr = str(candValue) if cand.text() == ' ' else ' '
                    cand.setText(candStr)
                    
                    return candValue
        
        return 0
        
    def mouseReleaseEvent(self, QMouseEvent):
        """ Handle cell being clicked on """
        
        cand = 0
        
        if self.property('selected') and self.cellString == ' ':
            cand = self.ToggleCandidateClicked()
        else: # Hightlight the cell in blue
            self.setProperty('selected', True)
            self.style().unpolish(self)
            self.style().polish(self)
            
        self.selected.emit(self, cand)
    
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
        # Span multiple columns / rows in order row, column, rowSpan, columnSpan
        # We will have 12 columns with first 9 being the sudoku board and last 
        # 3 the UI.  
        outerLayout.addLayout(gridLayout,0,0,9,9)
        self.CreateBoard(board, candBoard, self, gridLayout)
        
        vLayout = QVBoxLayout()
        # The UI will start at row 2 and be 4 rows rows deep
        outerLayout.addLayout(vLayout,2,9,4,3)
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
                bi, bj =  i//3, j//3
                parentBox = boxes[bi][bj]
                self.cells[i][j] = Cell(parentBox, Value2String(board[i][j]), candSet, i, j)
                self.cells[i][j].ConnectCelltoWindow(self.CellClicked)
                parentBox.AddCell(self.cells[i][j], i - 3*bi, j-3*bj)                
                
    def CreateButtons(self, parent, layout):
        """ Create the buttons toolbar for solving options """
        self.msgText = QLabel('Num Solutions: ?')
        self.msgText.setStyleSheet("border: 1px solid black;")
        layout.addWidget(self.msgText)
        
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

        updCandButton = QPushButton('Update Candidates')
        updCandButton.clicked.connect(lambda: self.UpdatePossibleCandidates())
        layout.addWidget(updCandButton)
        
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
        
        boxtriplePairButton = QPushButton('Highlight Box Triples')
        boxtriplePairButton.clicked.connect(lambda: self.HighlightBoxTriples())
        layout.addWidget(boxtriplePairButton)
        
        xwingButton = QPushButton('X-Wings')
        xwingButton.clicked.connect(lambda: self.HighlightXWings())
        layout.addWidget(xwingButton)
        
        clearHiliteButton = QPushButton('Clear Highlights')
        clearHiliteButton.clicked.connect(lambda: self.ClearHighlights())
        layout.addWidget(clearHiliteButton)
        

        
        
                
    def CellClicked(self, cell, cand):
        """ Handler function for a cell being clicked.  Makes sure only 1 cell
        is selected at a time ie only 1 cell has focus for input. """
        if self.selectedCell and self.selectedCell is not cell:
            self.selectedCell.Deselect()
   
        self.selectedCell = cell
        
        valStr = ', with value '+self.selectedCell.cellString if self.selectedCell else ''
        candStr = ', changed candidate '+str(cand) if cand > 0 else ''
        
        if cand > 0:
            i,j = self.selectedCell.i, self.selectedCell.j
            if cand in self.candBoard[i][j]:
                self.candBoard[i][j].remove(cand)
            else:
                self.candBoard[i][j].add(cand)
        
        print ('Clicked on cell ('+str(self.selectedCell.i)+','\
         +str(self.selectedCell.j)+')'+valStr+candStr)
          
                
    def FillinCell(self, i, j, value):
        """ Will fill in value in a cell if it is empty/unknown """
        
        self.cells[i][j].UpdateValue(Value2String(value))
        
        
    def RemoveCandidatesBasedonCellValue(self, i, j, value):
        """ If have assigned a value to cell i,j then remove the value as a 
        candidates from the block, row and column of that cell """

        bi, bj = i//3, j//3
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
        """ Update the display of changed cells and remove candidates that 
        are no longer valid due to the new values filled in """
        for i in range(0,9):
            for j in range(0,9):
                if prevBoard[i][j] != self.currBoard[i][j]:
                    self.FillinCell(i, j, self.currBoard[i][j])
                    self.RemoveCandidatesBasedonCellValue(i, j, self.currBoard[i][j])
 
    def Solve(self):
        """ Solves the board using the backtracking alogorithm """       
        if sd.BoardSolved(self.currBoard):
            return
        
        self.ClearHighlights()
        dups = sd.FindDuplicates(self.currBoard)
        
        NumSolns = 0
        
        if sd.CheckValid(dups):
            self.FillinSingleCandidates()
            prevBoard = deepcopy(self.currBoard)
            
            print('Start Solver')
            NumSolns, solnBoard = sd.SolvewBacktrack(self.currBoard)
            print('End Solver')
            
            if NumSolns == 0:
                print('No solution')
                self.msgText.setText('Num Solutions: 0')
            elif NumSolns == 1:
                self.currBoard = solnBoard
                self.UpdateChangedCells(prevBoard)
                
                dups = sd.FindDuplicates(self.currBoard)
                if not sd.CheckValid(dups):
                    print('Invalid')
                    NumSolns = 0
                else:
                    print('Single Solution')
            else:
                print('Multiple Solutions')
                
        if NumSolns == 1:
            self.msgText.setStyleSheet("border: 1px solid black; color: black;")
        else: 
            self.msgText.setStyleSheet("border: 1px solid black; color: red;")               
                
        self.msgText.setText('Num Solutions: '+str(NumSolns))

                    
        self.ShowInvalidCells(dups)
            
    def FillinSingleCandidatesStep(self):
        """ Look for cells with only 1 candidate and fill them in.
        Updates the candidates after finished """
        self.ClearHighlights()
        dups = sd.FindDuplicates(self.currBoard)
        if sd.CheckValid(dups):
            prevBoard = deepcopy(self.currBoard)
            
            changed, self.currBoard, self.candBoard = sd.FillSingleCandidates(self.currBoard, self.candBoard)
            if changed:
                self.UpdateChangedCells(prevBoard)
            
            dups = sd.FindDuplicates(self.currBoard)
            if not sd.CheckValid(dups):
                print('Invalid')
                
        self.ShowInvalidCells(dups)

        
    def FillinSingleCandidates(self):
        """ Look for cells with only 1 candidate and fill them in 
        Then update candidates and iterate until no more changes """
        self.ClearHighlights()
        dups = sd.FindDuplicates(self.currBoard)
        if sd.CheckValid(dups):
            notdone = True
            
            prevBoard = deepcopy(self.currBoard)
            
            while notdone:
                notdone, self.currBoard, self.candBoard = sd.FillSingleCandidates(self.currBoard, self.candBoard)
    
            self.UpdateChangedCells(prevBoard)
                        
            dups = sd.FindDuplicates(self.currBoard)
            if not sd.CheckValid(dups):
                print('Invalid')
                
        self.ShowInvalidCells(dups)
        
    def ClearHighlights(self):
        """ Remove all highlight from candidatyes """
        for i in range(0,9):
            for j in range(0,9):
                self.cells[i][j].ClearHilites()
        
    def HighlightHiddenSingles(self):
        """ Highlight where there are hidden single candidates """
        self.ClearHighlights()
        hiddenSingles = sd.HiddenSingles(self.currBoard, self.candBoard)
                
        for hiddenSingle in hiddenSingles:
            i,j,n = hiddenSingle
            self.cells[i][j].HiliteCandidates(set([n]))
            
    def HighlightNakedPairs(self):
        """ Highlight where there are naked pair candidates """
        self.ClearHighlights()
        pairSets, rCands = sd.NakedPairs(self.currBoard, self.candBoard)
        
        for pairSet in pairSets:
            a,b,i1,j1,i2,j2 = pairSet
            self.cells[i1][j1].HiliteCandidates(set([a,b]))
            self.cells[i2][j2].HiliteCandidates(set([a,b]))
            
        self.HighlightRemovals(rCands)
            
    def HighlightRemovals(self, rCands):
        """ Highlight candidates that can be removed based on list rCands """
        for rCand in rCands:
            n, i, j = rCand
            self.cells[i][j].HiliteCandidates(set([n]), colour='red')
            
    def HighlightPointingPairs(self):
        """ Highlight where there are pointing pair candidates """
        self.ClearHighlights()
        
        pairSets, rCands = sd.PointingPairs(self.currBoard, self.candBoard)
        
        for pairSet in pairSets:
            n,i1,j1,i2,j2 = pairSet
            self.cells[i1][j1].HiliteCandidates(set([n]))
            self.cells[i2][j2].HiliteCandidates(set([n]))
            
        self.HighlightRemovals(rCands)
            
    def HighlightBoxLinePairs(self):
        """ Highlight where there are box-line pair candidates """
        self.ClearHighlights()
        pairSets, rCands = sd.BoxLinePairs(self.currBoard, self.candBoard)
        
        for pairSet in pairSets:
            n,i1,j1,i2,j2 = pairSet
            self.cells[i1][j1].HiliteCandidates(set([n]))
            self.cells[i2][j2].HiliteCandidates(set([n]))

        self.HighlightRemovals(rCands)
        
    def HighlightBoxTriples(self):
        """ Highlight where there are box triple candidates """
        self.ClearHighlights()
        trips, rCands = sd.BoxTriples(self.currBoard, self.candBoard)
               
        for trip in trips:
            print(trip)
            a,b,c,(i1,j1),(i2,j2),(i3,j3) = trip
            self.cells[i1][j1].HiliteCandidates(set([a,b,c]) & self.candBoard[i1][j1])
            self.cells[i2][j2].HiliteCandidates(set([a,b,c]) & self.candBoard[i2][j2])
            self.cells[i3][j3].HiliteCandidates(set([a,b,c]) & self.candBoard[i3][j3])
            
        self.HighlightRemovals(rCands)
        
    def HighlightXWings(self):
        self.ClearHighlights()
        xwings, rCands = sd.XWings(self.currBoard, self.candBoard)
        
        for xwing in xwings:
            print(xwing)
            n, (i1,j1),(i2,j2),(i3,j3),(i4,j4) = xwing
            self.cells[i1][j1].HiliteCandidates(set([n]) & self.candBoard[i1][j1])
            self.cells[i2][j2].HiliteCandidates(set([n]) & self.candBoard[i2][j2])
            self.cells[i3][j3].HiliteCandidates(set([n]) & self.candBoard[i3][j3])
            self.cells[i4][j4].HiliteCandidates(set([n]) & self.candBoard[i4][j4])
        
        self.HighlightRemovals(rCands)

    
    def RegenerateCandidates(self):
        """ Reset the displayed candidates to those based on those that are 
        valid (ie avoid duplicates). Resets any candidate changes based on other
        patterns like hidden singles etc. """
        self.ClearHighlights()
        self.candBoard = sd.SolveCandidates(self.currBoard)
        
        for i in range(0,9):
            for j in range(0,9):
                candSet = self.candBoard[i][j]     
                self.cells[i][j].UpdateCandidates(candSet)  
                
    def UpdatePossibleCandidates(self):
        """ Removes any candidates that are no longer valid. 
        Does NOT reset candidate changes made previously """
        self.ClearHighlights()
        cands = sd.SolveCandidatesIntersect(self.currBoard, self.candBoard)        
        
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
                print('Invalid', dups)
            
            self.ShowInvalidCells(dups)
                

###############################################################################
# Main App function - creates the app and window then passes control to the 
# app GUI.  Returns when app quits

def run_app(origBoard):
    """ Main application function """
    print('Board is valid:', sd.BoardIsValid(origBoard))
    
    candBoard = sd.SolveCandidates(origBoard)

    app = QtWidgets.QApplication(sys.argv)
    mainWin = SudokuMainWindow(origBoard, candBoard)
    mainWin.show()
    
    return app.exec_()


###############################################################################

def UnitTests():
    print('######### Unit Tests #############')
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
    
    ns, sb = sd.SolvewBacktrack(testboard)
    print('Num Solutions in Test Board, should be 1:', ns)
    
    testboard[4][4] = 3    
    print('Check valid via Row Duplicate Test. Should be False:', \
        sd.BoardIsValid(testboard))
    
    testboard[4][4] = 7
    print('Check valid via Col Duplicate Test. Should be False:', \
        sd.BoardIsValid(testboard))
    
    testboard[4][4] = 5
    testboard[8][8] = 1
    print('Check valid via Block Duplicate Test. Should be False:', \
        sd.BoardIsValid(testboard))

    ns, sb = sd.SolvewBacktrack(testboard)
    print('Num Solutions in Invalid Test Board, should be 0:', ns)

    testboard = [
    [7,8,0,4,0,0,1,2,0],
    [6,0,0,0,7,5,0,0,9],
    [0,0,0,6,0,1,0,7,8],
    [0,0,7,0,4,0,2,6,0],
    [0,0,1,0,5,0,9,3,0],
    [9,0,4,0,6,0,0,0,5],
    [0,7,0,3,0,0,0,1,2],
    [1,2,0,0,0,0,4,0,0],
    [0,0,0,0,0,0,0,0,0]
    ]
    
    ns, sb = sd.SolvewBacktrack(testboard)
    print('Num Solutions in Incomplete Test Board, should be > 1:', ns)

    
    print('######### End Unit Tests #############')

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
    
    vhardboard = [
    [5,0,0,6,0,0,0,0,0],
    [0,6,0,0,0,3,9,0,0],
    [9,0,0,0,4,0,0,0,1],
    [7,1,0,0,5,0,0,0,0],
    [0,0,0,0,0,0,4,0,5],
    [0,0,0,0,2,0,7,1,3],
    [6,0,0,0,1,0,0,0,0],
    [0,0,8,2,0,0,0,6,0],
    [0,0,3,0,0,4,0,0,7]
    ]   
    
    xwingboard = [
    [6,0,0,0,9,0,0,0,7],
    [0,4,0,0,0,7,1,0,0],
    [0,0,2,8,0,0,0,5,0],
    [8,0,0,0,0,0,0,9,0],
    [0,0,0,0,7,0,0,0,0],
    [0,3,0,0,0,0,0,0,8],
    [0,5,0,0,0,2,3,0,0],
    [0,0,4,5,0,0,0,2,0],
    [9,0,0,0,3,0,0,0,4]
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
    sys.exit(run_app(xwingboard))