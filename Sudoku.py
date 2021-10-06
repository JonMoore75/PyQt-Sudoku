from copy import deepcopy


###############################################################################
# Sudoku Model - These functions deal with the board, its candidates and
# solutions


def GetRowCells(board, i):
    """ Get cells of row i """
    return board[i]


def GetColCells(board, j):
    """ Get cells of column j """
    return [row[j] for row in board]


def GetBlockIDFromCellCoords(i, j):
    return 3*(i // 3) + (j // 3)


def GetBlockCoordsFromBlockID(b):
    """ Find the block coords from for a 3x3 block labelled b. """
    return b // 3, b % 3


def GetCellCoordsFromBlockID(b, k):
    """ Find the board coords from for a particular cell in a 3x3 block.
        b - is the ID of the 3x3 block
        k - is the int cell id of the required cell in the 3x3 block
    Cell and block IDs are integers 0-8 labelling each cell in the 3x3 block or 3x3 block in the board in this pattern
     0 1 2
     3 4 5
     6 7 8
    """
    bi, bj = GetBlockCoordsFromBlockID(b)
    return 3*bi + k // 3, 3*bj + k % 3


def GetBlockCells_BlockID(board, b):
    """ Get the cells of a 3x3 block, where block b is labelled by number 0-8 in
    this pattern
     0 1 2
     3 4 5
     6 7 8
     """
    # Get the cells of a 3x3 block based on block coords bi and bj, and return the cells as a list
    bi, bj = GetBlockCoordsFromBlockID(b)
    return [board[bi * 3 + ci][bj * 3 + cj] for ci in range(0, 3) for cj in range(0, 3)]


def GetBlockCells_CellID(board, i, j):
    b = GetBlockIDFromCellCoords(i, j)
    return GetBlockCells_BlockID(board, b)


###############################################################################


def CheckListForDuplicates(list_of_cells):
    """ Check if given list contains any duplicates.  Achieves this by comparing the list to a set made from the list.
     The set contains only one of each unique value from the list.  If the list has a different length then it must
     contain duplicates """
    return len(list_of_cells) != len(set(list_of_cells))


def FindRowDuplicates(board):
    """ Loop thro each row and return location of any duplicate numbers as a list of tuple coord (i,j) pairs """
    duplicates = []

    for i in range(0, 9):
        row_i = GetRowCells(board, i)
        for n in range(1, 10):
            if row_i.count(n) > 1:
                duplicates += [(i, j) for j, cell_value in enumerate(row_i) if cell_value == n]

    return duplicates


def FindColDuplicates(board):
    """ Loop thro each column and return location of any duplicate numbers as a list of tuple coord (i,j) pairs """
    duplicates = []

    for j in range(0, 9):
        col_j = GetColCells(board, j)
        for n in range(1, 10):
            if col_j.count(n) > 1:
                duplicates += [(i, j) for i, cell_value in enumerate(col_j) if cell_value == n]

    return duplicates


def FindBlockDuplicates(board):
    """ Loop thro each block and return location of any duplicate numbers as a list of tuple coord (i,j) pairs """
    duplicates = []

    for b in range(0, 9):  # Loop thro each of the 9 3x3 blocks in the board
        block = GetBlockCells_BlockID(board, b)

        for n in range(1, 10):  # For each possible number n that could go in a cell
            if block.count(n) > 1:
                duplicates += [GetCellCoordsFromBlockID(b, k) for k, cell_value in enumerate(block) if cell_value == n]

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

def RemoveZeros(input_list):
    """ Remove zeros from a list, returns only non-zero values """
    return list(filter(lambda a: a != 0, input_list))


def GetCellCandidateList(board, i, j):
    """ Find possible values in a cell """

    block_values = set(RemoveZeros(GetBlockCells_CellID(board, i, j)))
    row_values = set(RemoveZeros(GetRowCells(board, i)))
    col_values = set(RemoveZeros(GetColCells(board, j)))

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

    b = GetBlockIDFromCellCoords(i, j)

    # Find indices of all cells in same col, row and block as cell (i,j)
    idx = {(i, rj) for rj in range(9)}                                       # Row
    idx = idx.union({(ri, j) for ri in range(9)})                            # Column
    idx = idx.union({GetCellCoordsFromBlockID(b, k) for k in range(0, 9)})   # Block
    idx.remove((i, j))

    # For each of these cells remove the value as a candidate
    for cds in idx:
        ci, cj = cds
        cand_board[ci][cj].discard(value)

    return cand_board


###############################################################################

def FindFirstEmptyCell(board):
    """ Find the first cell that is unknown empty """
    for i in range(0, 9):
        for j in range(0, 9):
            if board[i][j] == 0:
                return i, j
    return None


def BoardSolved(board):
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
                    i, j, n = value
                    board[i][j] = n
                    cand_board = UpdateCandidates(n, i, j, cand_board)

    #  Do backtrack solving but use the list of candidates in each cell to reduce search depth
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


###############################################################################

def FindHiddenSingle(board, cand_board, UnitFunc, CoordFunc):
    """ Find if row, column or block has only 1 cell a particular number can
    go into. """
    values = []

    # Search through 9 cell unit (row, column or block)
    for u in range(0, 9):
        cells = UnitFunc(board, u)
        candsInUnit = UnitFunc(cand_board, u)

        # Loop through all possible numbers
        for n in range(1, 10):
            count = 0
            idx = None
            for c in range(0, 9):
                if cells[c] == 0 and n in candsInUnit[c]:
                    count += 1
                    idx = c

            if count == 1:
                i, j = CoordFunc(u, idx)
                values += [(i, j, n)]

    return values


def HiddenSingles(board, cand_board):
    """ Find hidden singles, ie situations where a number has only one cell
    it can go in on a row, column or block """

    # Rows
    values = FindHiddenSingle(board, cand_board, GetRowCells, lambda b, k: (b, k))
    # Columns
    values += FindHiddenSingle(board, cand_board, GetColCells, lambda b, k: (k, b))
    # Block
    values += FindHiddenSingle(board, cand_board, GetBlockCells_BlockID, GetCellCoordsFromBlockID)

    return values


def FindNakedPair(board, cand_board, UnitFunc, CoordFunc):
    """ Finds cells with just 2 candidates in a cell where that pattern is
    repeated  once in same row, block or column ie 1 2, 1 2
    Means same values cannot be in other cells along that row, block or column
    """
    values, removal_values = [], []

    # Search through 9 cell unit (row, column or block)
    for u in range(0, 9):
        pairs = []
        pair_loc = []

        cells = UnitFunc(board, u)
        cands = UnitFunc(cand_board, u)

        # Loop through each cell of unit see if any pairs (cells with 2 cands)
        for c in range(0, 9):
            if len(cands[c]) == 2:
                # Get the values of the pair (a,b) and record location (i,j)
                it = iter(cands[c])
                a, b = next(it), next(it)
                i, j = CoordFunc(u, c)

                # If match previously found pair we have a Naked Pair
                for p, pair in enumerate(pairs):
                    i1, j1 = pair_loc[p][0], pair_loc[p][1]
                    if (a, b) == pair:
                        values += [(a, b, i1, j1, i, j)]

                        # Mark candidates with value n in same row/col/block for removal
                        removal_values += RemovalCandidates(cells, cands, a, lambda k: CoordFunc(u, k), [(i1, j1), (i, j)])
                        removal_values += RemovalCandidates(cells, cands, b, lambda k: CoordFunc(u, k), [(i1, j1), (i, j)])

                # Remember this pair
                pairs += [(a, b)]
                pair_loc += [(i, j)]

    return values, removal_values


def NakedPairs(board, cand_board):
    # Rows
    values_row, removal_values_row = FindNakedPair(board, cand_board, GetRowCells, lambda b, k: (b, k))

    # Columns
    values_col, removal_values_col = FindNakedPair(board, cand_board, GetColCells, lambda b, k: (k, b))

    # Blocks
    values_block, removal_values_block = FindNakedPair(board, cand_board, GetBlockCells_BlockID, GetCellCoordsFromBlockID)

    return values_row + values_col + values_block, removal_values_row + removal_values_col + removal_values_block


def FindBoxLinePair(board, cand_board, UnitFunc, isRow):
    """ Finds all box-line pairs in columns or rows.
    Box-line pair is when a particular number can only be in two cells on that row/column,
    both of which are in the same block.  Means can eliminate that candidate in
    that same block in other rows/columns. """
    values, removal_values = [], []

    # Search through 9 cell unit (row or column)
    for u in range(0, 9):
        cells = UnitFunc(board, u)
        candsInUnit = UnitFunc(cand_board, u)

        # Loop through all possible numbers
        for n in range(1, 10):
            count = 0
            idx = []

            # Loop through each cell of the unit
            for c in range(0, 9):
                if cells[c] == 0 and n in candsInUnit[c]:
                    count += 1
                    idx += [c]

            # If only found number n twice in col or row, check if in same block
            if count == 2:
                if idx[0] // 3 == idx[1] // 3:
                    if isRow:
                        i1, j1, i2, j2 = u, idx[0], u, idx[1]
                    else:
                        i1, j1, i2, j2 = idx[0], u, idx[1], u
                    values += [(n, i1, j1, i2, j2)]

                    # Mark candidates with value n in same block for removal
                    b = GetBlockIDFromCellCoords(i1, j1)
                    rcells = GetBlockCells_BlockID(board, b)
                    rcands = GetBlockCells_BlockID(cand_board, b)

                    def LocFunc(k):
                        return GetCellCoordsFromBlockID(b, k)
                    removal_values += RemovalCandidates(rcells, rcands, n, LocFunc, [(i1, j1), (i2, j2)])

    return values, removal_values


def BoxLinePairs(board, cand_board):
    values_row, removal_values_row = FindBoxLinePair(board, cand_board, GetRowCells, isRow=True)
    values_col, removal_values_col = FindBoxLinePair(board, cand_board, GetColCells, isRow=False)

    return values_row + values_col, removal_values_row + removal_values_col


def PointingPairs(board, cand_board):
    """ Finds all pointing pairs in either rows or columns.
    Pointing pair is if the only 2 cells a particular number can go in a block
    happen to be in same row or column. Means can eliminate that number as
    candidate in that row/column outside the block."""
    values, removal_values = [], []

    # Loop through each block
    for b in range(0, 9):
        cellsInBlock = GetBlockCells_BlockID(board, b)
        candsInBlock = GetBlockCells_BlockID(cand_board, b)

        # Loop through all possible numbers
        for n in range(1, 10):
            count = 0
            idx = []

            # Loop through each cell of the block
            for c in range(0, 9):
                if cellsInBlock[c] == 0 and n in candsInBlock[c]:
                    count += 1
                    idx += [c]

            # If only found number n twice in col or row, check if in same row/col
            if count == 2:
                i1, j1 = GetCellCoordsFromBlockID(b, idx[0])
                i2, j2 = GetCellCoordsFromBlockID(b, idx[1])

                if i1 == i2 or j1 == j2:
                    values += [(n, i1, j1, i2, j2)]

                    # Mark candidates with value n in same row/col for removal
                    rcells = GetRowCells(board, i1) if i1 == i2 else GetColCells(board, j1)
                    rcands = GetRowCells(cand_board, i1) if i1 == i2 else GetColCells(cand_board, j1)

                    def LocFunc(rc):
                        return (i1, rc) if i1 == i2 else (rc, j1)
                    removal_values += RemovalCandidates(rcells, rcands, n, LocFunc, [(i1, j1), (i2, j2)])

    return values, removal_values


def FindBoxTriples(board, cand_board, UnitFunc, CoordFunc):
    """ Finds all box triples.  This is where only 3 candidates in a given block row or column.  Means we can remove
    the same candidates in the same row/col outie the block. """

    values, removal_values = [], []

    # For each row/col
    for u in range(0, 9):
        cells = UnitFunc(board, u)      # Cells in this row or column only
        cands = UnitFunc(cand_board, u)  # Cands in this row or column only

        # Loop thro each set of 3 cells in each block in this row/col
        for b in range(0, 3):
            tripCandSet = set()
            bs = 3*b
            bf = bs + 3

            # If no cells filled in for this row/col in this block
            if cells[bs:bf] == [0, 0, 0]:
                for c in range(0, 3):               # Must be loop as cands is list of sets and
                    tripCandSet |= cands[bs + c]    # adds the candidates to the set via union operator

                # If only 3 possible candidates in these 3 cells
                if len(tripCandSet) == 3:
                    trip_loc = [CoordFunc(u, bs + k) for k in range(0, 3)]
                    x, y, z = tripCandSet
                    values += [tuple(tripCandSet) + tuple(trip_loc)]

                    # Mark candidates with value n in same row/col for removal
                    rcells = UnitFunc(board, u)
                    removal_values += RemovalCandidates(rcells, cands, x, lambda k: CoordFunc(u, k), trip_loc)
                    removal_values += RemovalCandidates(rcells, cands, y, lambda k: CoordFunc(u, k), trip_loc)
                    removal_values += RemovalCandidates(rcells, cands, z, lambda k: CoordFunc(u, k), trip_loc)

                    # Mark candidates with value n in same block for removal
                    b = GetBlockIDFromCellCoords(trip_loc[0][0], trip_loc[0][1])
                    rbcells = GetBlockCells_BlockID(board, b)
                    rbcands = GetBlockCells_BlockID(cand_board, b)
                    removal_values += RemovalCandidates(rbcells, rbcands, x, lambda k: GetCellCoordsFromBlockID(b, k), trip_loc)
                    removal_values += RemovalCandidates(rbcells, rbcands, y, lambda k: GetCellCoordsFromBlockID(b, k), trip_loc)
                    removal_values += RemovalCandidates(rbcells, rbcands, z, lambda k: GetCellCoordsFromBlockID(b, k), trip_loc)

    return values, removal_values


def BoxTriples(board, cand_board):
    # Rows
    values_row, removal_values_row = FindBoxTriples(board, cand_board, GetRowCells, lambda u, k: (u, k))
    # Columns
    values_col, removal_values_col = FindBoxTriples(board, cand_board, GetColCells, lambda u, k: (k, u))

    return values_row + values_col, removal_values_row + removal_values_col


def FindXWing(board, cand_board, UnitFunc, CoordFunc):
    values = []

    # Loop through all possible numbers
    for n in range(1, 10):

        pair_loc = []

        # For each row/col
        for u in range(0, 9):
            cells = UnitFunc(board, u)  # Cells in this row or column only
            cands = UnitFunc(cand_board, u)  # Cands in this row or column only

            count = 0
            idx = []

            # Loop through each cell of the unit
            for c in range(0, 9):
                if cells[c] == 0 and n in cands[c]:
                    count += 1
                    idx += [c]

            if count == 2:
                for pair in pair_loc:
                    ep, idxp = pair
                    if idxp == idx:
                        values += [(n, CoordFunc(u, idx[0]), CoordFunc(u, idx[1]), CoordFunc(ep, idxp[0]),
                                    CoordFunc(ep, idxp[1]))]
                pair_loc += [(u, idx)]

    return values


def XWingRemovals(board, cand_board, xwings):
    removal_values = []
    for xwing in xwings:
        n, (i1, j1), (i2, j2), (i3, j3), (i4, j4) = xwing

        rows = list({i1, i2, i3, i4})
        cols = list({j1, j2, j3, j4})

        for row in rows:
            row_cells = GetRowCells(board, row)
            row_cands = GetRowCells(cand_board, row)

            for col in range(0, 9):
                if col not in cols and row_cells[col] == 0 and n in row_cands[col]:
                    removal_values += [(n, row, col)]

        for col in cols:
            col_cells = GetColCells(board, col)
            col_cands = GetColCells(cand_board, col)

            for row in range(0, 9):
                if row not in rows and col_cells[row] == 0 and n in col_cands[row]:
                    removal_values += [(n, row, col)]

    return removal_values


def XWings(board, cand_board):
    # Rows
    row_values = FindXWing(board, cand_board, GetRowCells, lambda b, k: (b, k))
    # Columns
    col_values = FindXWing(board, cand_board, GetColCells, lambda b, k: (k, b))

    values = row_values + col_values

    removal_values = XWingRemovals(board, cand_board, values)

    return values, removal_values


def RemovalCandidates(unit_cells, candidates, n, LocFunc, exclusion_list):
    """ Marks all candidates with value n for removal if not in exclusion list.
    cells           - list of ints containing the values in the cells in the given unit (row, col, block)
    candidates      - list of sets of ints representing candidates for each cell
    LocFunc         - function that translates the 0->9 index to i,j cell coords
    n               - number (int) to be removed
    exclusion_list  - list of cells coords excluded from removal.

    The exclusion list is for the cells that cause the removal (ie orig pointing
    pair or similar) to avoid candidates causing their own removal.
    """
    removal_values = []

    assert(len(unit_cells) == 9)

    # Loop through each cell of the block
    for i, cell in enumerate(unit_cells):
        ri, rj = LocFunc(i)

        if cell == 0 and n in candidates[i] and (ri, rj) not in exclusion_list:
            removal_values += [(n, ri, rj)]

    return removal_values
