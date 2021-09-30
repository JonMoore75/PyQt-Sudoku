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


def GetBlockCoordsFromCellCoords(i, j):
    """ Find the block coords from for a 3x3 block labelled b. """
    return i // 3, j // 3


def GetBlockCoordsFromBlockLabel(b):
    """ Find the block coords from for a 3x3 block labelled b. """
    return b // 3, b % 3


def GetCellCoordsFromBlockCoords(bi, bj, k):
    """ Find the board coords from for a particular cell in a 3x3 block.
        bi, bj - int coords of the 3x3 block e.g. (0,0) is top left and (2,2) bottom right block
        k - is the int cell label of the required cell in the 3x3 block

    Cell labels are integers 0-9 labelling each cell in the 3x3 block in this pattern
     0 1 2
     3 4 5
     6 7 8

    We use these 3 coords to find the i,j int coords of the cell in the whole board
    """
    return 3*bi + k // 3, 3*bj + k % 3


def GetCellCoordsFromBlockLabel(b, k):
    """ Find the board coords from for a particular cell in a 3x3 block. """
    bi, bj = GetBlockCoordsFromBlockLabel(b)
    return GetCellCoordsFromBlockCoords(bi, bj, k)


def GetBlockCells_coords(board, bi, bj):
    """ Get the cells of a 3x3 block based on block coords bi and bj, and return the cells as a list"""
    return [board[bi * 3 + ci][bj * 3 + cj] for ci in range(0, 3) for cj in range(0, 3)]


def GetBlockCells_BlockLabel(board, b):
    """ Get the cells of a 3x3 block, where block b is labelled by number 0-9 in
    this pattern
     0 1 2
     3 4 5
     6 7 8
     """
    bi, bj = GetBlockCoordsFromBlockLabel(b)
    return GetBlockCells_coords(board, bi, bj)


def GetBlockCells(board, i, j):
    bi, bj = GetBlockCoordsFromCellCoords(i, j)
    return GetBlockCells_coords(board, bi, bj)


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
        block = GetBlockCells_BlockLabel(board, b)

        for n in range(1, 10):  # For each possible number n that could go in a cell
            if block.count(n) > 1:
                duplicates += [GetCellCoordsFromBlockLabel(b, k) for k, cell_value in enumerate(block) if cell_value == n]

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

    blockValues = set(RemoveZeros(GetBlockCells(board, i, j)))
    rowValues = set(RemoveZeros(GetRowCells(board, i)))
    colValues = set(RemoveZeros(GetColCells(board, j)))

    return set(range(1, 10)) - blockValues - rowValues - colValues


def FillSingleCandidates(board, candBoard):
    """ Fills in any empty cells with single candidate
    Copies inputs so not changed by this function."""
    board_copy = deepcopy(board)
    changed = False

    for i in range(0, 9):
        for j in range(0, 9):
            if len(candBoard[i][j]) == 1 and board[i][j] == 0:
                changed = True
                board_copy[i][j] = next(iter(candBoard[i][j]))

    return changed, board_copy, SolveCandidatesIntersect(board_copy, candBoard)


def SolveCandidates(board):
    """ Takes a Sudoku board (2d 9x9 list of ints with 0 as empty cell) and
    returns a board that is a 2d 9x9 list of sets.  Each set is the possible
    int values. Known values are now sets with 1 item. """
    candBoard = [[{} for i in range(9)] for j in range(9)]
    for i in range(0, 9):
        for j in range(0, 9):
            if board[i][j] == 0:
                candBoard[i][j] = GetCellCandidateList(board, i, j)
            else:
                candBoard[i][j] = set([board[i][j]])
    return candBoard


def SolveCandidatesIntersect(board, origCandBoard):
    """ Takes a Sudoku board (2d 9x9 list of ints with 0 as empty cell) and
    returns a board that is a 2d 9x9 list of sets.  Each set is the possible
    int values. Known values are now sets with 1 item. This version compares to
    the previous candidates and returns only candidates in both sets"""
    candBoard = deepcopy(origCandBoard)
    for i in range(0, 9):
        for j in range(0, 9):
            if board[i][j] == 0:
                candSet = GetCellCandidateList(board, i, j)
                candBoard[i][j] = candBoard[i][j].intersection(candSet)
            else:
                candBoard[i][j] = set([board[i][j]])
    return candBoard


def UpdateCandidates(value, i, j, origCandBoard):
    """ If a value has been filled in at cell i,j then remove that as a candidate
    from the same col, row and block. """
    candBoard = deepcopy(origCandBoard)
    candBoard[i][j] = {value}

    bi, bj = GetBlockCoordsFromCellCoords(i,j)

    # Find indices of all cells in same col, row and block
    idx = {(i, rj) for rj in range(9)}                                                  # Row
    idx = idx.union({(ri, j) for ri in range(9)})                                       # Column
    idx = idx.union({GetCellCoordsFromBlockCoords(bi, bj, bk) for bk in range(0, 9)})   # Block

    idx.remove((i, j))

    # For each of these cells remove the value as a candidate
    for cds in idx:
        ci, cj = cds
        candBoard[ci][cj].discard(value)

    return candBoard


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
    numSolns = 0
    solnBoard = None

    if initial:
        candBoard = SolveCandidates(board)
        changed = True
        while changed:
            changed = False
            changed, board, candBoard = FillSingleCandidates(board, candBoard)
            values = HiddenSingles(board, candBoard)

            # Fill in hidden singles
            if len(values) > 0:
                changed = True

                for value in values:
                    i, j, n = value
                    board[i][j] = n
                    candBoard = UpdateCandidates(n, i, j, candBoard)

    found_empty_cell = FindFirstEmptyCell(board)
    if found_empty_cell:
        i, j = found_empty_cell
        candSet = GetCellCandidateList(board, i, j)

        for cand in iter(candSet):
            # Try solution
            board[i][j] = cand

            numSolns_loop, solnBoard_loop = SolvewBacktrack(board, False)
            numSolns += numSolns_loop
            if numSolns == 1 and solnBoard_loop is not None:
                solnBoard = solnBoard_loop

            board[i][j] = 0

        return numSolns, solnBoard
    else:
        return 1, deepcopy(board)  # Solved!


###############################################################################

def FindHiddenSingle(board, candBoard, UnitFunc, CoordFunc):
    """ Find if row, column or block has only 1 cell a particular number can
    go into. """
    values = []

    # Search through 9 cell unit (row, column or block)
    for e in range(0, 9):
        cells = UnitFunc(board, e)
        candsInUnit = UnitFunc(candBoard, e)

        # Loop through all possible numbers
        for n in range(1, 10):
            count = 0
            idx = None
            for c in range(0, 9):
                if cells[c] == 0 and n in candsInUnit[c]:
                    count += 1
                    idx = c

            if count == 1:
                i, j = CoordFunc(e, idx)
                values += [(i, j, n)]

    return values


def HiddenSingles(board, candBoard):
    """ Find hidden singles, ie situations where a number has only one cell
    it can go in on a row, column or block """

    # Rows
    values = FindHiddenSingle(board, candBoard, GetRowCells, lambda b, k: (b, k))
    # Columns
    values += FindHiddenSingle(board, candBoard, GetColCells, lambda b, k: (k, b))
    # Block
    values += FindHiddenSingle(board, candBoard, GetBlockCells_BlockLabel, GetCellCoordsFromBlockLabel)

    return values


def FindNakedPair(board, candBoard, UnitFunc, CoordFunc):
    """ Finds cells with just 2 candidates in a cell where that pattern is
    repeated  once in same row, block or column ie 1 2, 1 2
    Means same values cannot be in other cells along that row, block or column
    """
    values, removal_values = [], []

    # Search through 9 cell unit (row, column or block)
    for u in range(0, 9):
        pairs = []
        pair_loc = []

        cands = UnitFunc(candBoard, u)

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
                        rcells = UnitFunc(board, u)
                        removal_values += RemovalCandidates(rcells, cands, a, lambda k: CoordFunc(u, k), [(i1, j1), (i, j)])
                        removal_values += RemovalCandidates(rcells, cands, b, lambda k: CoordFunc(u, k), [(i1, j1), (i, j)])

                # Remember this pair
                pairs += [(a, b)]
                pair_loc += [(i, j)]

    return values, removal_values


def NakedPairs(board, candBoard):
    # Rows
    valuesR, rvaluesR = FindNakedPair(board, candBoard, GetRowCells, lambda b, k: (b, k))

    # Columns
    valuesC, rvaluesC = FindNakedPair(board, candBoard, GetColCells, lambda b, k: (k, b))

    # Blocks
    valuesB, rvaluesB = FindNakedPair(board, candBoard, GetBlockCells_BlockLabel, GetCellCoordsFromBlockLabel)

    return valuesR + valuesC + valuesB, rvaluesR + rvaluesC + rvaluesB


def FindBoxLinePair(board, candBoard, UnitFunc, isRow):
    """ Finds all box-line pairs in columns or rows.
    Box-line pair is when a particular number can only be in two cells on that row/column,
    both of which are in the same block.  Means can eliminate that candidate in
    that same block in other rows/columns. """
    values, removal_values = [], []

    # Search through 9 cell unit (row, column or block)
    for e in range(0, 9):
        cells = UnitFunc(board, e)
        candsInUnit = UnitFunc(candBoard, e)

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
                        i1, j1, i2, j2 = e, idx[0], e, idx[1]
                    else:
                        i1, j1, i2, j2 = idx[0], e, idx[1], e
                    values += [(n, i1, j1, i2, j2)]

                    # Mark candidates with value n in same block for removal
                    bi, bj = GetBlockCoordsFromCellCoords(i1, j1)
                    rcells = GetBlockCells_coords(board, bi, bj)
                    rcands = GetBlockCells_coords(candBoard, bi, bj)

                    def LocFunc(k):
                        return GetCellCoordsFromBlockCoords(bi, bj, k)
                    removal_values += RemovalCandidates(rcells, rcands, n, LocFunc, [(i1, j1), (i2, j2)])

    return values, removal_values


def BoxLinePairs(board, candBoard):
    valuesR, rvaluesR = FindBoxLinePair(board, candBoard, GetRowCells, isRow=True)
    valuesC, rvaluesC = FindBoxLinePair(board, candBoard, GetColCells, isRow=False)

    return valuesR + valuesC, rvaluesR + rvaluesC


def PointingPairs(board, candBoard):
    """ Finds all pointing pairs in either rows or columns.
    Pointing pair is if the only 2 cells a particular number can go in a block
    happen to be in same row or column. Means can eliminate that number as
    candidate in that row/column outside the block."""
    values, removal_values = [], []

    # Loop through each block
    for b in range(0, 9):
        cellsInBlock = GetBlockCells_BlockLabel(board, b)
        candsInBlock = GetBlockCells_BlockLabel(candBoard, b)

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
                i1, j1 = GetCellCoordsFromBlockLabel(b, idx[0])
                i2, j2 = GetCellCoordsFromBlockLabel(b, idx[1])

                if i1 == i2 or j1 == j2:
                    values += [(n, i1, j1, i2, j2)]

                    # Mark candidates with value n in same row/col for removal
                    rcells = GetRowCells(board, i1) if i1 == i2 else GetColCells(board, j1)
                    rcands = GetRowCells(candBoard, i1) if i1 == i2 else GetColCells(candBoard, j1)

                    def LocFunc(rc):
                        return (i1, rc) if i1 == i2 else (rc, j1)
                    removal_values += RemovalCandidates(rcells, rcands, n, LocFunc, [(i1, j1), (i2, j2)])

    return values, removal_values


def FindBoxTriples(board, candBoard, UnitFunc, CoordFunc):
    """ Finds all box triples.  This is where only 3 candidates in a given block row or column.  Means we can remove
    the same candidates in the same row/col outie the block. """

    values, removal_values = [], []

    # For each row/col
    for u in range(0, 9):
        cells = UnitFunc(board, u)      # Cells in this row or column only
        cands = UnitFunc(candBoard, u)  # Cands in this row or column only

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
                    bi, bj = GetBlockCoordsFromCellCoords(trip_loc[0][0], trip_loc[0][1])
                    rbcells = GetBlockCells_coords(board, bi, bj)
                    rbcands = GetBlockCells_coords(candBoard, bi, bj)
                    removal_values += RemovalCandidates(rbcells, rbcands, x, lambda k: GetCellCoordsFromBlockCoords(bi, bj, k), trip_loc)
                    removal_values += RemovalCandidates(rbcells, rbcands, y, lambda k: GetCellCoordsFromBlockCoords(bi, bj, k), trip_loc)
                    removal_values += RemovalCandidates(rbcells, rbcands, z, lambda k: GetCellCoordsFromBlockCoords(bi, bj, k), trip_loc)

    return values, removal_values


def BoxTriples(board, candBoard):
    # Rows
    valuesR, rvaluesR = FindBoxTriples(board, candBoard, GetRowCells, lambda u, k: (u, k))
    # Columns
    valuesC, rvaluesC = FindBoxTriples(board, candBoard, GetColCells, lambda u, k: (k, u))

    return valuesR + valuesC, rvaluesR + rvaluesC


def FindXWing(board, candBoard, UnitFunc, CoordFunc):
    values = []

    # Loop through all possible numbers
    for n in range(1, 10):

        pair_loc = []

        # For each row/col
        for u in range(0, 9):
            cells = UnitFunc(board, u)  # Cells in this row or column only
            cands = UnitFunc(candBoard, u)  # Cands in this row or column only

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


def XWingRemovals(board, candBoard, xwings):
    removal_values = []
    for xwing in xwings:
        n, (i1, j1), (i2, j2), (i3, j3), (i4, j4) = xwing

        rows = list({i1, i2, i3, i4})
        cols = list({j1, j2, j3, j4})

        for row in rows:
            rowCells = GetRowCells(board, row)
            rowCands = GetRowCells(candBoard, row)

            for col in range(0, 9):
                if col not in cols and rowCells[col] == 0 and n in rowCands[col]:
                    removal_values += [(n, row, col)]

        for col in cols:
            colCells = GetColCells(board, col)
            colCands = GetColCells(candBoard, col)

            for row in range(0, 9):
                if row not in rows and colCells[row] == 0 and n in colCands[row]:
                    removal_values += [(n, row, col)]

    return removal_values


def XWings(board, candBoard):
    # Rows
    row_values = FindXWing(board, candBoard, GetRowCells, lambda b, k: (b, k))
    # Columns
    col_values = FindXWing(board, candBoard, GetColCells, lambda b, k: (k, b))

    values = row_values + col_values

    removal_values = XWingRemovals(board, candBoard, values)

    return values, removal_values


def RemovalCandidates(cells, candidates, n, LocFunc, exclusion_list):
    """ List the candidates to be marked for removal.
    cells           - list of ints containing the values in the cells
    candidates      - list of sets of ints representing candidates for each cell
    LocFunc         - function that translates the 0->9 index to i,j cell coords
    n               - number (int) to be removed
    exclusion_list  - list of cells coords excluded from removal.

    The exclusion list is for the cells that cause the removal (ie orig pointing
    pair or similar) to avoid candidates causing their own removal.
    """
    rvalues = []

    # Loop through each cell of the block
    for candidate_for_removal in range(0, 9):
        ri, rj = LocFunc(candidate_for_removal)

        if cells[candidate_for_removal] == 0 and n in candidates[candidate_for_removal]:
            if (ri, rj) not in exclusion_list:
                rvalues += [(n, ri, rj)]

    return rvalues
