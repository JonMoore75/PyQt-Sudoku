from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QGridLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal, pyqtSlot


Signal, Slot = pyqtSignal, pyqtSlot


def Value2String(value):
    return str(value) if (0 < value < 10) else ' '


class Candidate(QLabel):
    def __init__(self, str_value, parent):
        super(QLabel, self).__init__(str_value, parent)
        self.setStyleSheet("""
           Candidate[hilite="red"]      {background-color: red;}
           Candidate[hilite="green"]    {background-color: lightgreen;}
           Candidate[hilite="off"]      {background: transparent;}
            """)

        self.SetHilite('off')

        self.setFont(QFont("Arial", 12))
        self.setAlignment(QtCore.Qt.AlignCenter)

    def SetHilite(self, hilite_colour='off'):
        """ Set or remove highlight for this candidate """
        self.setProperty('hilite', hilite_colour)
        self.style().unpolish(self)
        self.style().polish(self)


class Cell(QLabel):
    # selected is a class to define the type of signals Cell can emit on mouse click
    selected = Signal(object, int)

    def __init__(self, parent, i, j, value=0):
        super(QLabel, self).__init__(Value2String(value), parent)
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
        self.SetEditStatus(value)

        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFont(QFont("Arial", 45, QFont.Bold))

        self.gridLayoutBox = QGridLayout()
        self.setLayout(self.gridLayoutBox)

    @staticmethod
    def CandCoordFromValue(value):
        return (value - 1) // 3, (value - 1) % 3

    def CreateCandidates(self, cand_set=set()):
        """ Create grid of QLabel widgets to display the candidates """
        for cand_value in range(1, 10):
            i, j = self.CandCoordFromValue(cand_value)
            cand_str = str(cand_value) if cand_value in cand_set else ' '
            cand_label = Candidate(cand_str, self)
            self.gridLayoutBox.addWidget(cand_label, i, j)

    def ConnectCelltoWindow(self, ClickFunc):
        """ Specifies the function to pass events to when this cell is clicked on by the
        mouse (signal called selected is emitted in mouseReleaseEvent below)"""
        self.selected.connect(ClickFunc)

    def CanEdit(self):
        return self.property('edit')

    def SetValidity(self, is_invalid):
        """ If the value in this cell conflicts with the value in another cell
        then highlight it """
        self.setProperty('invalid', is_invalid)
        self.style().unpolish(self)
        self.style().polish(self)

    def UpdateValue(self, value, initial=False):
        """ Will fill in value in a cell if it is empty/unknown """
        str_value = Value2String(value)
        if initial:
            self.SetEditStatus(str_value)

        if self.CanEdit() or initial:
            if str_value != ' ':
                self.DeleteAllCandidates()
            else:
                self.CreateCandidates()

            self.setText(str_value)

    def SetEditStatus(self, str_value):
        if str_value == ' ':
            self.setProperty('edit', True)
        else:
            self.setProperty('edit', False)
        self.style().unpolish(self)
        self.style().polish(self)

    def DeleteAllCandidates(self):
        for i in reversed(range(self.gridLayoutBox.count())):
            widget = self.gridLayoutBox.itemAt(i).widget()
            widget.setParent(None)
            widget.deleteLater()

    def UpdateCandidates(self, cand_set):
        """ Updates the valid candidates for empty/unknown cell """
        if self.text() == ' ':
            for cand_value in range(1, 10):
                i, j = self.CandCoordFromValue(cand_value)
                cand_widget = self.gridLayoutBox.itemAtPosition(i, j).widget()
                cand_str = str(cand_value) if cand_value in cand_set else ' '
                cand_widget.setText(cand_str)

    def HiliteCandidates(self, cand_set, colour='green'):
        """ Highlight candidates in this cell given by candSet """
        if self.text() == ' ':
            for cand_value in iter(cand_set):
                i, j = self.CandCoordFromValue(cand_value)
                cand_widget = self.gridLayoutBox.itemAtPosition(i, j).widget()
                cand_widget.SetHilite(colour)

    def ClearHilites(self):
        """ Remove any candidate highlighting from this cell """
        if self.text() == ' ':
            for cand in range(1, 10):
                i, j = (cand - 1) // 3, (cand - 1) % 3
                cand_widget = self.gridLayoutBox.itemAtPosition(i, j).widget()
                cand_widget.SetHilite('off')

    def RemoveCandidate(self, value):
        """ Removes candidate value from empty/unknown cell """
        if self.text() == ' ':
            i, j = self.CandCoordFromValue(value)
            cand_widget = self.gridLayoutBox.itemAtPosition(i, j).widget()
            cand_widget.setText(' ')

    def ToggleCandidateClicked(self):
        """ Toggles the candidate number if under the mouse """
        if self.text() == ' ':
            for cand_value in range(1, 10):
                i, j = self.CandCoordFromValue(cand_value)
                cand_widget = self.gridLayoutBox.itemAtPosition(i, j).widget()
                if cand_widget.underMouse():
                    cand_str = str(cand_value) if cand_widget.text() == ' ' else ' '
                    cand_widget.setText(cand_str)
                    return cand_value

        return 0

    def mouseReleaseEvent(self, QMouseEvent):
        """ Handle cell being clicked on.  Will find if a candidate has been clicked, if so cand set the number (1-9)
         of the candidate clciked.  If no valid candidate cand=0.
         This cell object and cand then emitted as a signal to connected slots (The main window class)
         """

        cand = 0

        # Toggle candidates if no value in cell
        if self.property('selected'):
            cand = self.ToggleCandidateClicked()

        # Hightlight the cell in blue to indicate this cell has keyboard focus
        if not self.property('selected'):
            self.setProperty('selected', True)
            self.style().unpolish(self)
            self.style().polish(self)

        self.selected.emit(self, cand)

    def Deselect(self):
        """ If cell selected, deselect it """
        self.setProperty('selected', False)
        self.style().unpolish(self)
        self.style().polish(self)


class Block(QLabel):
    def __init__(self, parent):
        super(QLabel, self).__init__(parent)
        self.setStyleSheet('background-color: lightgrey;')

        self.gridLayoutBox = QGridLayout()
        self.setLayout(self.gridLayoutBox)

    def AddCell(self, cell_QLabel, i, j):
        self.gridLayoutBox.addWidget(cell_QLabel, i, j)