from copy import deepcopy
import sudoku_coords as sdc
from sudoku_pattern import HiddenSingles


###############################################################################
# Board validity code


def FindUnitDuplicates(unit_list, coord_func):
    """ Loop thro each unit (row or col etc) and return location of any duplicate numbers as a list of
    tuple coord (i,j) pairs """
    duplicates = []
    for u, unit_cells in enumerate(unit_list):
        duplicated_numbers = [n for n in range(1, 10) if unit_cells.count(n) > 1]
        duplicates += [coord_func(u, c) for n in duplicated_numbers for c, elem in enumerate(unit_cells) if elem == n]

    return duplicates


def FindDuplicates(board):
    """ Find duplicate entries on any row, column or block """

    row_duplicates = FindUnitDuplicates(board, sdc.GetCellCoordsFromRowID)
    col_duplicates = FindUnitDuplicates([sdc.GetColCells(board, j) for j in range(0, 9)], sdc.GetCellCoordsFromColID)
    block_duplicates = FindUnitDuplicates([sdc.GetBlockCells_BlockID(board, b) for b in range(0, 9)],
                                          sdc.GetCellCoordsFromBlockID)

    return row_duplicates + col_duplicates + block_duplicates


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


def GetCellCandidateSet(board, i, j):
    """ Find possible values in a cell """

    if board[i][j] == 0:
        block_values = set(RemoveZeros(sdc.GetBlockCells_CellID(board, i, j)))
        row_values = set(RemoveZeros(sdc.GetRowCells(board, i)))
        col_values = set(RemoveZeros(sdc.GetColCells(board, j)))

        return set(range(1, 10)) - block_values - row_values - col_values
    else:
        return {board[i][j]}


def SolveCandidates(board):
    """ Takes a Sudoku board (2d 9x9 list of ints with 0 as empty cell) and
    returns a board that is a 2d 9x9 list of sets.  Each set is the possible
    int values. Known values are now sets with 1 item. """
    cand_board = [[GetCellCandidateSet(board, i, j) for j in range(9)] for i in range(9)]
    return cand_board


def SolveCandidatesIntersect(board, orig_cand_board):
    """ Takes a Sudoku board (2d 9x9 list of ints with 0 as empty cell) and
    returns a board that is a 2d 9x9 list of sets.  Each set is the possible
    int values. Known values are now sets with 1 item.
    This version compares to the previous candidates and returns only
    candidates in both sets.
    This prevents candidates previously removed from being added back."""

    def solve_cell_candidates(i, j):
        possible_candidates = GetCellCandidateSet(board, i, j)
        return orig_cand_board[i][j].intersection(possible_candidates)

    return [[solve_cell_candidates(i, j) for j in range(9)] for i in range(9)]


def UpdateCandidates(value, i, j, orig_cand_board):
    """ If a value has been filled in at cell i,j then remove that as a candidate
    from the same col, row and block. """
    cand_board = deepcopy(orig_cand_board)
    cand_board[i][j] = {value}

    b = sdc.GetBlockIDFromCellCoords(i, j)

    # Find indices of all cells in same col, row and block as cell (i,j)
    idx = {(i, rj) for rj in range(9)}  # Row
    idx = idx.union({(ri, j) for ri in range(9)})  # Column
    idx = idx.union({sdc.GetCellCoordsFromBlockID(b, k) for k in range(0, 9)})  # Block
    idx.remove((i, j))

    # For each of these cells remove the value as a candidate
    for cds in idx:
        ci, cj = cds
        cand_board[ci][cj].discard(value)

    return cand_board


###############################################################################
# Solving code

def FindFirstEmptyCell(board):
    """ Find the coords of first cell that has an unknown value (indicated by zero) """
    # Define iterator that tracks across each row looking for zeroes, then find the first zero using next()
    zero_iter = ((i, j) for i, row in enumerate(board) for j, cell_value in enumerate(row) if cell_value == 0)
    return next(zero_iter, None)


def BoardSolved(board):
    """ Check all cells have a value.  Assumes board is valid. """
    return FindFirstEmptyCell(board) is None


def FillinSingleCandidates_iterative(board, cand_board):
    """ Fill in cells with only a single candidate iteratively until no more to fill in """
    single_candidates = [(i, j) for i in range(9) for j in range(9) if len(cand_board[i][j]) == 1 and board[i][j] == 0]
    if len(single_candidates) > 0:
        for i, j in single_candidates:
            board[i][j] = next(iter(cand_board[i][j]))
        cand_board = SolveCandidatesIntersect(board, cand_board)

        # Repeat until no changes needed
        board, cand_board = FillinSingleCandidates_iterative(board, cand_board)

    return board, cand_board


def FillinHiddenSingles_iterative(board, cand_board):
    """ Fill in hidden single candidates iteratively until no more to fill in """
    hidden_singles = HiddenSingles(board, cand_board)
    if len(hidden_singles) > 0:

        for hidden_single in hidden_singles:
            i, j, n = hidden_single.i, hidden_single.j, next(iter(hidden_single.candidates))
            board[i][j] = n
            cand_board = UpdateCandidates(n, i, j, cand_board)

        # Repeat until no changes needed
        board, cand_board = FillinSingleCandidates_iterative(board, cand_board)

    return board, cand_board


def SolvewBacktrack(board, initial=True):
    """ Solve the puzzle via the backtracking algorithm """
    num_solns = 0
    soln_board = None

    board_copy = deepcopy(board)

    # First simplify the board by filling in naked and hidden singles
    if initial:
        cand_board = SolveCandidates(board_copy)
        board_copy, cand_board = FillinSingleCandidates_iterative(board_copy, cand_board)
        board_copy, cand_board = FillinHiddenSingles_iterative(board_copy, cand_board)

    #  Do backtrack solving but use the list of candidates in each cell to reduce search depth
    #  Start by finding the first cell that has no known value, if all cells have values then board solved.
    first_empty_cell = FindFirstEmptyCell(board_copy)
    if first_empty_cell is not None:
        i, j = first_empty_cell
        possible_candidates = GetCellCandidateSet(board_copy, i, j)

        for candidate in iter(possible_candidates):
            # Try solution
            board_copy[i][j] = candidate

            num_solns_loop, soln_board_loop = SolvewBacktrack(board_copy, initial=False)
            num_solns += num_solns_loop
            if num_solns == 1 and soln_board_loop is not None:
                soln_board = soln_board_loop

            board_copy[i][j] = 0

        return num_solns, soln_board
    else:
        return 1, deepcopy(board_copy)  # Solved!
