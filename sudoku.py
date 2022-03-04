from copy import deepcopy
import sudoku_coords as sdc
from sudoku_pattern import HiddenSingles

###############################################################################
# Board validity code


def CheckListForDuplicates(list_of_cells):
    """ Check if given list contains any duplicates.  Achieves this by comparing the list to a set made from the list.
     The set contains only one of each unique value from the list.  If the list has a different length then it must
     contain duplicates """
    return len(list_of_cells) != len(set(list_of_cells))


def FindRowDuplicates(board):
    """ Loop thro each row and return location of any duplicate numbers as a list of tuple coord (i,j) pairs """
    duplicates = []

    for i in range(0, 9):
        row_i = sdc.GetRowCells(board, i)
        for n in range(1, 10):
            if row_i.count(n) > 1:
                duplicates += [(i, j) for j, cell_value in enumerate(row_i) if cell_value == n]

    return duplicates


def FindColDuplicates(board):
    """ Loop thro each column and return location of any duplicate numbers as a list of tuple coord (i,j) pairs """
    duplicates = []

    for j in range(0, 9):
        col_j = sdc.GetColCells(board, j)
        for n in range(1, 10):
            if col_j.count(n) > 1:
                duplicates += [(i, j) for i, cell_value in enumerate(col_j) if cell_value == n]

    return duplicates


def FindBlockDuplicates(board):
    """ Loop thro each block and return location of any duplicate numbers as a list of tuple coord (i,j) pairs """
    duplicates = []

    for b in range(0, 9):  # Loop thro each of the 9 3x3 blocks in the board
        block = sdc.GetBlockCells_BlockID(board, b)

        for n in range(1, 10):  # For each possible number n that could go in a cell
            if block.count(n) > 1:
                duplicates += [sdc.GetCellCoordsFromBlockID(b, k) for k, cell_value in enumerate(block) if cell_value == n]

    return duplicates


def FindDuplicates(board):
    """ Find duplicate entries on any row, column or block """
    return FindRowDuplicates(board) + FindColDuplicates(board) + FindBlockDuplicates(board)


def CheckValid(list_of_duplicates):
    """ If no duplicates then the board is valid.  This does not indicate if the
    board has a unique solution """
    return len(list_of_duplicates) == 0


def BoardIsValid(board):
    return CheckValid(FindDuplicates(board))


###############################################################################
# Candidate code

def RemoveZeros(input_list):
    """ Remove zeros from a list, returns only non-zero values """
    return list(filter(lambda a: a != 0, input_list))


def GetCellCandidateList(board, i, j):
    """ Find possible values in a cell """

    block_values = set(RemoveZeros(sdc.GetBlockCells_CellID(board, i, j)))
    row_values = set(RemoveZeros(sdc.GetRowCells(board, i)))
    col_values = set(RemoveZeros(sdc.GetColCells(board, j)))

    return set(range(1, 10)) - block_values - row_values - col_values


def FillSingleCandidates(board, cand_board):
    """ Fills in any empty cells with single candidate
    Copies inputs so not changed by this function."""
    board_copy = deepcopy(board)
    changed = False

    for i in range(0, 9):
        for j in range(0, 9):
            if len(cand_board[i][j]) == 1 and board[i][j] == 0:
                changed = True
                board_copy[i][j] = next(iter(cand_board[i][j]))

    return changed, board_copy, SolveCandidatesIntersect(board_copy, cand_board)


def SolveCandidates(board):
    """ Takes a Sudoku board (2d 9x9 list of ints with 0 as empty cell) and
    returns a board that is a 2d 9x9 list of sets.  Each set is the possible
    int values. Known values are now sets with 1 item. """
    cand_board = [[{} for i in range(9)] for j in range(9)]
    for i in range(0, 9):
        for j in range(0, 9):
            if board[i][j] == 0:
                cand_board[i][j] = GetCellCandidateList(board, i, j)
            else:
                cand_board[i][j] = set([board[i][j]])
    return cand_board


def SolveCandidatesIntersect(board, orig_cand_board):
    """ Takes a Sudoku board (2d 9x9 list of ints with 0 as empty cell) and
    returns a board that is a 2d 9x9 list of sets.  Each set is the possible
    int values. Known values are now sets with 1 item.
    This version compares to the previous candidates and returns only
    candidates in both sets.
    This prevents candidates previously removed from being added back."""
    cand_board = deepcopy(orig_cand_board)
    for i in range(0, 9):
        for j in range(0, 9):
            if board[i][j] == 0:
                candSet = GetCellCandidateList(board, i, j)
                cand_board[i][j] = cand_board[i][j].intersection(candSet)
            else:
                cand_board[i][j] = set([board[i][j]])
    return cand_board


def UpdateCandidates(value, i, j, orig_cand_board):
    """ If a value has been filled in at cell i,j then remove that as a candidate
    from the same col, row and block. """
    cand_board = deepcopy(orig_cand_board)
    cand_board[i][j] = {value}

    b = sdc.GetBlockIDFromCellCoords(i, j)

    # Find indices of all cells in same col, row and block as cell (i,j)
    idx = {(i, rj) for rj in range(9)}                                       # Row
    idx = idx.union({(ri, j) for ri in range(9)})                            # Column
    idx = idx.union({sdc.GetCellCoordsFromBlockID(b, k) for k in range(0, 9)})   # Block
    idx.remove((i, j))

    # For each of these cells remove the value as a candidate
    for cds in idx:
        ci, cj = cds
        cand_board[ci][cj].discard(value)

    return cand_board


###############################################################################
# Solving code

def FindFirstEmptyCell(board):
    """ Find the first cell that has a unknown value """
    for i in range(0, 9):
        for j in range(0, 9):
            if board[i][j] == 0:
                return i, j
    return None


def BoardSolved(board):
    """ Check all cells have a value.  Assumes board is valid. """
    return FindFirstEmptyCell(board) is None


def SolvewBacktrack(board, initial=True):
    """ Solve the puzzle via the backtracking algorithm """
    num_solns = 0
    soln_board = None

    # First simplify the board by filling in naked and hidden singles
    if initial:
        cand_board = SolveCandidates(board)
        changed = True
        while changed:
            changed = False
            changed, board, cand_board = FillSingleCandidates(board, cand_board)
            values = HiddenSingles(board, cand_board)

            # Fill in hidden singles
            if len(values) > 0:
                changed = True

                for value in values:
                    i, j, n = value.i, value.j, next(iter(value.candidates))
                    board[i][j] = n
                    cand_board = UpdateCandidates(n, i, j, cand_board)

    #  Do backtrack solving but use the list of candidates in each cell to reduce search depth
    #  Start by finding the first cell that has no known value, if all cells have values then board solved.
    found_empty_cell = FindFirstEmptyCell(board)
    if found_empty_cell:
        i, j = found_empty_cell
        candSet = GetCellCandidateList(board, i, j)

        for cand in iter(candSet):
            # Try solution
            board[i][j] = cand

            num_solns_loop, soln_board_loop = SolvewBacktrack(board, False)
            num_solns += num_solns_loop
            if num_solns == 1 and soln_board_loop is not None:
                soln_board = soln_board_loop

            board[i][j] = 0

        return num_solns, soln_board
    else:
        return 1, deepcopy(board)  # Solved!



