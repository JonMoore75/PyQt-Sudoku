from PyQtView import Cmds


class Controller:
    def __init__(self, _model, _view):
        self.model = _model
        self.view = _view

        self.selected_cell = None

        self.view.Connect({})

    def CellValueUpdated(self, value):
        """ Called when user inputs a new value for a cell """
        if self.selected_cell:
            i, j = self.selected_cell
            cell = self.view.cells[i][j]

            if cell.CanEdit() and self.model.board[i][j] != value:
                self.model.board[i][j] = value
                cell.UpdateValue(value)

    def CellValueDeleted(self):
        """ Called when user deletes a value from a cell """
        self.CellValueUpdated(self, 0)

    def MouseClick(self):
        """ If user clicks mouse but NOT on a cell or button then deselect any selected cell """
        if self.selected_cell:
            self.selected_cell.Deselect()

        self.selected_cell = None

    def CellClicked(self, clicked_cell):
        if self.selected_cell and self.selected_cell != clicked_cell:
            self.selected_cell.Deselect()

        self.selected_cell = clicked_cell

        # If candidate clicked then toggle it
        cand = clicked_cell.ToggleCandidateClicked()
        if cand > 0:
            i, j = self.selected_cell.i, self.selected_cell.j
            if cand in self.model.cand_board[i][j]:
                self.model.cand_board[i][j].remove(cand)
            else:
                self.model.cand_board[i][j].add(cand)

        value_str = ', with value ' + clicked_cell.text() if clicked_cell else ''
        cand_str = ', changed candidate ' + str(cand) if cand > 0 else ''

        print('Clicked on cell (' + str(clicked_cell.i) + ','
              + str(clicked_cell.j) + ')' + value_str + cand_str)

