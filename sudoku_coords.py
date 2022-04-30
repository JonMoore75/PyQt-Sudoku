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


def GetCellCoordsFromRowID(r, k):
    return r, k


def GetCellCoordsFromColID(c, k):
    return k, c


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