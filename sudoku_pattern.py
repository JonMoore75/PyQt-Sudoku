from dataclasses import dataclass
from sudoku_coords import GetRowCells, GetColCells, GetBlockCells_BlockID, GetCellCoordsFromBlockID, \
                            GetBlockIDFromCellCoords, GetCellCoordsFromColID, GetCellCoordsFromRowID

###############################################################################


@dataclass
class PatternInfo:
    i: int
    j: int
    candidates: {int}


def FindHiddenSingle(board, cand_board, unit_func, coord_func):
    """ Find if row, column or block has only 1 cell a particular number can
    go into. """
    values = []

    # Search through 9 cell unit (row, column or block)
    for u in range(0, 9):
        cells = unit_func(board, u)
        candsInUnit = unit_func(cand_board, u)

        # Loop through all possible numbers
        for n in range(1, 10):
            idx = [c for c in range(0, 9) if cells[c] == 0 and n in candsInUnit[c]]

            if len(idx) == 1:
                i, j = coord_func(u, idx[0])
                values.append(PatternInfo(i, j, {n}))

    return values


def HiddenSingles(board, cand_board):
    """ Find hidden singles, ie situations where a number has only one cell
    it can go in on a row, column or block """

    # Rows
    values = FindHiddenSingle(board, cand_board, GetRowCells, GetCellCoordsFromRowID)
    # Columns
    values += FindHiddenSingle(board, cand_board, GetColCells, GetCellCoordsFromColID)
    # Block
    values += FindHiddenSingle(board, cand_board, GetBlockCells_BlockID, GetCellCoordsFromBlockID)

    return values


def FindNakedPair(board, cand_board, unit_func, coord_func):
    """ Finds cells with just 2 candidates in a cell where that pattern is
    repeated  once in same row, block or column ie 1 2, 1 2
    Means same values cannot be in other cells along that row, block or column
    """
    values, removal_values = [], []

    # Search through 9 cell unit (row, column or block)
    for u in range(0, 9):
        pairs = []
        pair_loc = []

        cells = unit_func(board, u)
        cands = unit_func(cand_board, u)

        # Loop through each cell of unit see if any pairs (cells with 2 cands)
        for c in range(0, 9):
            if len(cands[c]) == 2:
                # Get the values of the pair (a,b) and record location (i,j)
                it = iter(cands[c])
                a, b = next(it), next(it)
                i, j = coord_func(u, c)

                # If match previously found pair we have a Naked Pair
                for p, pair in enumerate(pairs):
                    i1, j1 = pair_loc[p]
                    if (a, b) == pair:
                        this_pattern = [PatternInfo(i, j, {a, b}), PatternInfo(i1, j1, {a, b})]
                        this_removals = RemovalCandidates(cells, cands, {a, b},
                                                                lambda k: coord_func(u, k), [(i1, j1), (i, j)])
                        if len(this_removals):
                            values += this_pattern
                            removal_values += this_removals

                # Remember this pair
                pairs += [(a, b)]
                pair_loc += [(i, j)]

    return values, removal_values


def NakedPairs(board, cand_board):
    # Rows
    values_row, removal_values_row = FindNakedPair(board, cand_board, GetRowCells, GetCellCoordsFromRowID)

    # Columns
    values_col, removal_values_col = FindNakedPair(board, cand_board, GetColCells, GetCellCoordsFromColID)

    # Blocks
    values_block, removal_values_block = FindNakedPair(board, cand_board, GetBlockCells_BlockID, GetCellCoordsFromBlockID)

    return values_row + values_col + values_block, removal_values_row + removal_values_col + removal_values_block


def FindBoxLinePair(board, cand_board, unit_func, isRow):
    """ Finds all box-line pairs in columns or rows.
    Box-line pair is when a particular number can only be in two cells on that row/column,
    both of which are in the same block.  Means can eliminate that candidate in
    that same block in other rows/columns. """
    values, removal_values = [], []

    # Search through 9 cell unit (row or column)
    for u in range(0, 9):
        cells = unit_func(board, u)
        candsInUnit = unit_func(cand_board, u)

        # Loop through all possible numbers
        for n in range(1, 10):
            # Find location of all candidates of value n
            idx = [c for c in range(0, 9) if cells[c] == 0 and n in candsInUnit[c]]

            # If only found number n twice in col or row and both in same block
            if len(idx) == 2 and idx[0] // 3 == idx[1] // 3:
                if isRow:
                    i1, j1, i2, j2 = u, idx[0], u, idx[1]
                else:
                    i1, j1, i2, j2 = idx[0], u, idx[1], u
                this_pattern = [PatternInfo(i1, j1, {n}), PatternInfo(i2, j2, {n})]

                # Mark candidates with value n in same block for removal
                b = GetBlockIDFromCellCoords(i1, j1)
                rcells = GetBlockCells_BlockID(board, b)
                rcands = GetBlockCells_BlockID(cand_board, b)

                def LocFunc(k):
                    return GetCellCoordsFromBlockID(b, k)
                this_removals = RemovalCandidates(rcells, rcands, {n}, LocFunc, [(i1, j1), (i2, j2)])

                if len(this_removals):
                    values += this_pattern
                    removal_values += this_removals

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
            idx = [c for c in range(0, 9) if cellsInBlock[c] == 0 and n in candsInBlock[c]]

            # If only found number n twice in col or row, check if in same row/col
            if len(idx) == 2:
                i1, j1 = GetCellCoordsFromBlockID(b, idx[0])
                i2, j2 = GetCellCoordsFromBlockID(b, idx[1])

                if i1 == i2 or j1 == j2:
                    this_pattern = [PatternInfo(i1, j1, {n}), PatternInfo(i2, j2, {n})]

                    # Mark candidates with value n in same row/col for removal
                    rcells = GetRowCells(board, i1) if i1 == i2 else GetColCells(board, j1)
                    rcands = GetRowCells(cand_board, i1) if i1 == i2 else GetColCells(cand_board, j1)

                    def LocFunc(rc):
                        return (i1, rc) if i1 == i2 else (rc, j1)
                    this_removals = RemovalCandidates(rcells, rcands, {n}, LocFunc, [(i1, j1), (i2, j2)])

                    if len(this_removals):
                        values += this_pattern
                        removal_values += this_removals

    return values, removal_values


def FindBoxTriples(board, cand_board, unit_func, coord_func):
    """ Finds all box triples.  This is where only 3 candidates in a given block, row or column.  Means we can remove
    the same candidates in the same row/col outside the block. """

    values, removal_values = [], []

    # For each row/col
    for u in range(0, 9):
        cells = unit_func(board, u)      # Cells in this row or column only
        cands = unit_func(cand_board, u)  # Cands in this row or column only

        # Loop thro each set of 3 cells in each block in this row/col
        for b in range(0, 3):
            cs = 3 * b

            # If no cells filled in for this row/col in this block
            if cells[cs:cs + 3] == [0, 0, 0]:
                tripCandSet = set().union(*cands[cs:cs + 3])  # Add these cells candidates to set using union operator

                # If only 3 possible candidates in these 3 cells
                if len(tripCandSet) == 3:
                    x, y, z = tripCandSet
                    trip_loc = [coord_func(u, cs + k) for k in range(0, 3)]
                    for k in range(0, 3):
                        this_pattern = [PatternInfo(*trip_loc[k], tripCandSet & cands[cs + k])]

                    # Mark candidates with value n in same row/col for removal
                    rcells = unit_func(board, u)
                    removal_values += RemovalCandidates(rcells, cands, {x, y, z}, lambda k: coord_func(u, k), trip_loc)

                    # Mark candidates with value n in same block for removal
                    bl = GetBlockIDFromCellCoords(*coord_func(u, cs))
                    rbcells = GetBlockCells_BlockID(board, bl)
                    rbcands = GetBlockCells_BlockID(cand_board, bl)
                    this_removals = RemovalCandidates(rbcells, rbcands, {x, y, z},
                                                        lambda k: GetCellCoordsFromBlockID(bl, k), trip_loc)
                    if len(this_removals):
                        values += this_pattern
                        removal_values += this_removals

    return values, removal_values


def BoxTriples(board, cand_board):
    # Rows
    values_row, removal_values_row = FindBoxTriples(board, cand_board, GetRowCells, GetCellCoordsFromRowID)
    # Columns
    values_col, removal_values_col = FindBoxTriples(board, cand_board, GetColCells, GetCellCoordsFromColID)

    return values_row + values_col, removal_values_row + removal_values_col


def FindXWing(board, cand_board, unit_func, coord_func):
    values, removal_values = [], []

    # Loop through all possible numbers
    for n in range(1, 10):

        pair_loc = []

        # For each row/col
        for u in range(0, 9):
            cells = unit_func(board, u)  # Cells in this row or column only
            cands = unit_func(cand_board, u)  # Cands in this row or column only

            idx = [c for c in range(0, 9) if cells[c] == 0 and n in cands[c]]

            # If just two places for n in this row/col, idx now a list of two location values
            # see if matching pair from another row/col to form a square pattern
            if len(idx) == 2:
                for pair in pair_loc:
                    u_p, idxp = pair
                    if idxp == idx:
                        this_pattern = [PatternInfo(*coord_func(u, idx[0]), {n}),
                                        PatternInfo(*coord_func(u, idx[1]), {n}),
                                        PatternInfo(*coord_func(u_p, idxp[0]), {n}),
                                        PatternInfo(*coord_func(u_p, idxp[1]), {n})]
                        this_removals = XWingRemovals(board, cand_board, this_pattern)

                        if len(this_removals):
                            values += this_pattern
                            removal_values += this_removals

                pair_loc += [(u, idx)]

    return values, removal_values


def XWingRemovals(board, cand_board, xwing):
    removal_values = []

    assert (len(xwing) == 4)
    xw1, xw2, xw3, xw4 = xwing
    n = next(iter(xw1.candidates))

    rows = list({xw1.i, xw2.i, xw3.i, xw4.i})
    cols = list({xw1.j, xw2.j, xw3.j, xw4.j})

    for row in rows:
        row_cells = GetRowCells(board, row)
        row_cands = GetRowCells(cand_board, row)

        for col in range(0, 9):
            if col not in cols and row_cells[col] == 0 and n in row_cands[col]:
                removal_values.append(PatternInfo(row, col, {n}))

    for col in cols:
        col_cells = GetColCells(board, col)
        col_cands = GetColCells(cand_board, col)

        for row in range(0, 9):
            if row not in rows and col_cells[row] == 0 and n in col_cands[row]:
                removal_values.append(PatternInfo(row, col, {n}))

    return removal_values


def XWings(board, cand_board):
    # Rows
    values_row,  removal_values_row = FindXWing(board, cand_board, GetRowCells, GetCellCoordsFromRowID)
    # Columns
    values_col, removal_values_col = FindXWing(board, cand_board, GetColCells, GetCellCoordsFromColID)

    assert(len(values_row + values_col) % 4 == 0)
    # xwings = [values[x:x+4] for x in range(0, len(values), 4)]
    # removal_values = XWingRemovals(board, cand_board, xwings)

    return values_row + values_col, removal_values_row + removal_values_col


def RemovalCandidates(unit_cells, candidates, values, LocFunc, exclusion_list):
    """ Marks all candidates with value n for removal if not in exclusion list.
    cells           - list of ints containing the values in the cells in the given unit (row, col, block)
    candidates      - list of sets of ints representing candidates for each cell
    LocFunc         - function that translates the 0->9 index to i,j cell coords
    values          - set of int values to be removed from the cells candidates
    exclusion_list  - list of cells coords excluded from removal.

    The exclusion list is for the cells that cause the removal (ie original pointing
    pair or similar) to avoid candidates causing their own removal.
    """
    removal_values = []

    assert(len(unit_cells) == 9)
    assert(type(values) is set)

    # Loop through each cell of the unit
    for i, cell in enumerate(unit_cells):
        ri, rj = LocFunc(i)

        values_in_cell = values & candidates[i]

        if cell == 0 and (ri, rj) not in exclusion_list and len(values_in_cell) > 0:
            removal_values.append(PatternInfo(ri, rj, values_in_cell))

    return removal_values