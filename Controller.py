from PyQtView import Cmds
import Sudoku as sd


class Controller:
    def __init__(self, _view, _model):
        func_map = {Cmds.NUM: self.SelectedCellValueUpdated,
                    Cmds.DEL: self.CellValueDeleted,
                    Cmds.MOUSE: self.MouseClick,
                    Cmds.CELLCLICK: self.CellClicked,
                    Cmds.RESTART: self.ResetBoard,
                    Cmds.SOLVE: self.Solve,
                    Cmds.FILLSINGLE: self.FillinSingleCandidatesStep,
                    Cmds.UPDATE: self.UpdatePossibleCandidates,
                    Cmds.HIDSINGLE: self.HighlightHiddenSingles,
                    Cmds.NAKEDPAIR: self.HighlightNakedPairs,
                    Cmds.POINTPAIR: self.HighlightPointingPairs,
                    Cmds.BOXLINE: self.HighlightBoxLinePairs,
                    Cmds.BOXTRIPLE: self.HighlightBoxTriples,
                    Cmds.XWING: self.HighlightXWings,
                    Cmds.REGEN: self.RegenerateCandidates,
                    Cmds.CLEAR: self.ClearHighlights}

        self.model = _model
        self.view = _view
        self.view.Connect(func_map)

        self.selected_cell = None

        self.ResetBoard()

    ####################################################################################################################

    def SelectedCellValueUpdated(self, value):
        """ Called when user inputs a new value for a cell """
        if self.selected_cell:
            i, j = self.selected_cell.i, self.selected_cell.j

            if self.selected_cell.CanEdit() and self.model.GetCell(i, j) != value:
                self.model.SetCell(i, j, value)
                self.selected_cell.UpdateValue(value)
                self.ShowInvalidCells()

    def CellValueDeleted(self):
        """ Called when user deletes a value from a cell """
        self.SelectedCellValueUpdated(0)

    def MouseClick(self):
        """ If user clicks mouse but NOT on a cell or button then deselect any selected cell """
        if self.selected_cell:
            self.selected_cell.Deselect()

        self.selected_cell = None

    def CellClicked(self, clicked_cell):
        """ Handler for clicking on a cell.  Cell receives the click and displays itself as selected
        then signals to this function.  Here the selected_cell is updated if changed, then look to see
        if click is on a candidate and if so toggle it. """
        cand = 0
        if self.selected_cell:
            if self.selected_cell is not clicked_cell:
                self.selected_cell.Deselect()
            else:
                cand = clicked_cell.FindCandidateClicked()

                # If candidate clicked then toggle it
                if cand > 0:
                    i, j = clicked_cell.i, clicked_cell.j
                    if cand in self.model.GetCands(i, j):
                        self.model.GetCands(i, j).remove(cand)
                        clicked_cell.RemoveCandidate(cand)
                    else:
                        self.model.GetCands(i, j).add(cand)
                        clicked_cell.AddCandidate(cand)

        self.selected_cell = clicked_cell

        value_str = ', with value ' + clicked_cell.text() if clicked_cell else ''
        cand_str = ', changed candidate ' + str(cand) if cand > 0 else ''

        print('Clicked on cell (' + str(clicked_cell.i) + ','
              + str(clicked_cell.j) + ')' + value_str + cand_str)

    ####################################################################################################################

    def ShowInvalidCells(self):
        dups = sd.FindDuplicates(self.model.GetBoard())
        self.view.ShowInvalidCells(dups)
        if not sd.CheckValid(dups):
            self.view.SetNumSolutions(-1)
        else:
            self.view.SetNumSolutions(None)

    ####################################################################################################################

    def ResetBoard(self):
        self.model.ResetBoard()
        self.view.UpdateAllCells(self.model.GetBoard(), initial=True)
        self.view.SetNumSolutions(None)
        self.ClearHighlights()
        self.RegenerateCandidates()
        self.ShowInvalidCells()

    def Solve(self):
        """ Solves the board using the backtracking algorithm """
        if sd.BoardSolved(self.model.curr_board):
            return

        num_solns = self.model.Solve()
        self.view.UpdateAllCells(self.model.GetBoard())
        self.ClearHighlights()
        self.ShowInvalidCells()
        self.view.SetNumSolutions(num_solns)

    def FillinSingleCandidatesStep(self):
        """ Look for cells with only 1 candidate and fill them in.
                Updates the candidates after finished """
        self.ClearHighlights()
        self.model.FillinSingleCandidatesStep()
        self.view.UpdateAllCells(self.model.GetBoard())
        self.view.UpdateAllCandidates(self.model.GetAllCands())
        self.ShowInvalidCells()

    def UpdatePossibleCandidates(self):
        """ Removes any candidates that are no longer valid.
        Does NOT reset candidate changes made previously """
        self.ClearHighlights()
        self.model.UpdateCandidates()
        self.view.UpdateAllCandidates(self.model.GetAllCands())

    def HighlightHiddenSingles(self):
        """ Highlight where there are hidden single candidates """
        self.ClearHighlights()
        hidden_singles = sd.HiddenSingles(self.model.GetBoard(), self.model.GetAllCands())
        self.view.HighlightValues(hidden_singles)

    def HighlightNakedPairs(self):
        """ Highlight where there are naked pair candidates """
        self.ClearHighlights()
        values, removals = sd.NakedPairs(self.model.GetBoard(), self.model.GetAllCands())

        self.view.HighlightValues(values)
        self.view.HighlightRemovals(removals)

    def HighlightPointingPairs(self):
        self.ClearHighlights()
        values, removals = sd.PointingPairs(self.model.GetBoard(), self.model.GetAllCands())

        self.view.HighlightValues(values)
        self.view.HighlightRemovals(removals)

    def HighlightBoxLinePairs(self):
        self.ClearHighlights()
        values, removals = sd.BoxLinePairs(self.model.GetBoard(), self.model.GetAllCands())

        self.view.HighlightValues(values)
        self.view.HighlightRemovals(removals)

    def HighlightBoxTriples(self):
        self.ClearHighlights()
        values, removals = sd.BoxTriples(self.model.GetBoard(), self.model.GetAllCands())

        self.view.HighlightValues(values)
        self.view.HighlightRemovals(removals)

    def HighlightXWings(self):
        self.ClearHighlights()
        values, removals = sd.XWings(self.model.GetBoard(), self.model.GetAllCands())

        self.view.HighlightValues(values)
        self.view.HighlightRemovals(removals)

    def RegenerateCandidates(self):
        """ Reset the displayed candidates to those based on those that are
            valid (ie avoid duplicates). Resets any candidate changes based on other
            patterns like hidden singles etc. """
        self.ClearHighlights()
        self.model.RegenCandidates()
        self.view.UpdateAllCandidates(self.model.GetAllCands())

    def ClearHighlights(self):
        """ Remove all highlight from candidates """
        self.view.ClearHighlights()
