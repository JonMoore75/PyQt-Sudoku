from copy import deepcopy
import sudoku as sd


class SudokuModel:
    def __init__(self, board):
        # Variables (Data)
        self.orig_board = board
        self.curr_board = deepcopy(board)
        self.cand_board = None

    def ResetBoard(self):
        self.curr_board = deepcopy(self.orig_board)
        self.cand_board = None

    def GetBoard(self):
        return self.curr_board

    def GetAllCands(self):
        return self.cand_board

    def GetCell(self, i, j):
        return self.curr_board[i][j]

    def GetCands(self, i, j):
        return self.cand_board[i][j]

    def SetCell(self, i, j, value):
        self.curr_board[i][j] = value

    def RegenCandidates(self):
        self.cand_board = sd.SolveCandidates(self.curr_board)

    def UpdateCandidates(self):
        self.cand_board = sd.SolveCandidatesIntersect(self.curr_board, self.cand_board)

    def FillinSingleCandidatesStep(self):
        """ Fills in any empty cells with only a single candidate """
        if not sd.BoardIsValid(self.curr_board):
            return

        for i in range(0, 9):
            for j in range(0, 9):
                if len(self.cand_board[i][j]) == 1 and self.curr_board[i][j] == 0:
                    self.curr_board[i][j] = next(iter(self.cand_board[i][j]))

        self.cand_board = sd.SolveCandidatesIntersect(self.curr_board, self.cand_board)

    def Solve(self):
        num_solns = 0

        if not sd.BoardIsValid(self.curr_board):
            print('Invalid')
            num_solns = -1
            return num_solns

        print('Start Solver')
        num_solns, soln_board = sd.SolvewBacktrack(self.curr_board)
        print('End Solver')

        # Prob not needed but here as a failsafe
        if num_solns == 0:
            print('No solution')
        elif num_solns == 1:
            print('Single Solution')
            self.curr_board = soln_board
        else:
            print('Multiple Solutions')

        return num_solns

