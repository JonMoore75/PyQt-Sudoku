from copy import deepcopy

###############################################################################
# Sudoku Model - These functions deal with the board, its candidates and 
# solutions 

def checkListForDuplicates(listOfCells):
    """ Check if given list contains any duplicates """
    return len(listOfCells) != len(set(listOfCells))

def FindRowDuplicates(board):
    """ If any duplicates numbers by row return location as (i,j) pairs """
    duplicates= []
    
    for i in range(0,9):
        row_i = board[i]
        for n in range(1,10):
            if row_i.count(n) > 1:
                duplicates += [(i,j) for j,x in enumerate(board[i]) if x == n]
        
    return duplicates
            
def FindColDuplicates(board):
    """ If any duplicates numbers by column return location as (i,j) pairs """    
    duplicates= []
    
    for j in range(0,9):
        col_j = [row[j] for row in board]
        for n in range(1,10):
            if col_j.count(n) > 1:
                duplicates += [(i,j) for i,x in enumerate(col_j) if x == n]
    
    return duplicates
    
def FindBlockDuplicates(board):
    """ If any duplicates numbers by block return location as (i,j) pairs """
    duplicates= []
    
    for b in range(0,9):
        bi, bj = b//3, b%3
        block = [board[bi*3 + ci][bj*3 + cj] for ci in range(0,3) for cj in range(0,3)]

        for n in range(1,10):
            if block.count(n) > 1:
                duplicates += [(3*bi+k//3,3*bj+k%3) for k,x in enumerate(block) if x == n]
            
    return duplicates

def FindDuplicates(board):
    """ Find duplicate entries on any row, column or block """
    return FindRowDuplicates(board) + \
        FindColDuplicates(board) + \
        FindBlockDuplicates(board)  
        
def CheckValid(dup):
    """ Pass in list of duplicates via dup (output of FindDuplicates()).  If 
    no duplicates then the board is valid.  This does not indicate if the 
    board has a unique solution """
    return len(dup) == 0

###############################################################################

def RemoveZeros(inputList):
    """ Remove zeros from a list, returns only non-zero values """
    return list(filter(lambda a: a != 0, inputList))

def GetCandidateList(board, i, j):
    """ Find possible values in a cell """
    bi = i//3
    bj = j//3
    
    block = [[board[bi*3 + ci][bj*3 + cj] for cj in range(0,3)] for ci in range(0,3)]
    row_i = board[i]
    col_j = [row[j] for row in board]
    
    blockValues = set(RemoveZeros([c for row in block for c in row]))
    rowValues = set(RemoveZeros(row_i))
    colValues = set(RemoveZeros(col_j))
    
    return set(range(1,10)) - blockValues - rowValues - colValues

def FillSingleCandidates(board, candBoard):
    """ Fills in any empty cells with single candidate 
    Copies inputs so not changed by this function."""
    boardcopy = deepcopy(board)
    changed = False
    
    for i in range(0,9):
        for j in range(0,9): 
            if len(candBoard[i][j]) == 1 and board[i][j] == 0:
                changed = True
                boardcopy[i][j] = next(iter(candBoard[i][j]))
    
    return changed, boardcopy, SolveCandidates(boardcopy)

def SolveCandidates(board):
    """ Takes a Sudoku board (2d 9x9 list of ints with 0 as empty cell) and 
    returns a board that is a 2d 9x9 list of sets.  Each set is the possible 
    int values. Known values are now sets with 1 item. """
    candBoard = deepcopy(board)
    for i in range(0,9):
        for j in range(0,9):
            if board[i][j] == 0:
                candBoard[i][j] = GetCandidateList(board, i, j)
            else:
                candBoard[i][j] = set([board[i][j]])
    return candBoard
###############################################################################

def FindEmpty(board):
    """ Find the first cell that is unknown empty """
    for i in range(0,9):
        for j in range(0,9):
            if board[i][j] == 0:
                return (i,j)
    return None

def SolvewBacktrack(board):
    """ Solve the puzzle via the backtracking algorithm """
    foundEmpty = FindEmpty(board)
    
    if not foundEmpty:
        return True # Solved!
    
    i,j = foundEmpty
    candSet = GetCandidateList(board, i, j)
    
    for cand in iter(candSet):
        
        board[i][j] = cand
        
        if SolvewBacktrack(board):
            return True
        
        board[i][j] = 0
        
    return False

###############################################################################

def RowCells(board, i):
    return board[i]

def ColCells(board, j):
    return [row[j] for row in board]

def BlockCells_coords(board, bi, bj):
    """ Get the cells of a block based on block coords """
    return [board[bi*3 + ci][bj*3 + cj] for ci in range(0,3) for cj in range(0,3)]

def BlockCells(board, b):
    """ Get the cells of a block, where block is labelled by number 0-9 in 
    this pattern
     0 1 2
     3 4 5
     6 7 8
     """
    bi, bj = b//3, b%3
    return BlockCells_coords(board, bi, bj)

def BlockCoords_coords(bi, bj, k):
    return 3*bi + k // 3, 3*bj + k % 3
    
def BlockCoords(b,k):
    bi, bj = b//3, b%3
    return BlockCoords_coords(bi, bj ,k)

def FindHiddenSingle(board, candBoard, ElemFunc, CoordFunc):
    """ Find if row, column or block has only 1 cell a particular number can
    go into. """
    values = []

    # Search through 9 cell element (row, column or block)
    for e in range(0,9):
        cells = ElemFunc(board, e) 
        candsInElem = ElemFunc(candBoard, e) 

        # Loop through all possible numbers
        for n in range(1,10):
            count = 0
            idx = None
            for c in range(0,9):
                if cells[c] == 0 and n in candsInElem[c]:
                    count += 1
                    idx = c 
                    
            if count == 1:
                i,j = CoordFunc(e,idx)
                values += [(i,j,n)]
                
    return values

def HiddenSingles(board, candBoard):
    """ Find hidden singles, ie situations where a number has only one cell 
    it can go in on a row, column or block """
    
    # Rows
    values = FindHiddenSingle(board, candBoard, RowCells, lambda b,k: (b,k))
    # Columns  
    values += FindHiddenSingle(board, candBoard, ColCells, lambda b,k: (k,b))  
    #Block
    values += FindHiddenSingle(board, candBoard, BlockCells, BlockCoords)  
                
    return values

def FindNakedPair(board, candBoard, ElemFunc, CoordFunc):
    """ Finds cells with just 2 candidates in a cell where that pattern is 
    repeated  once in same row, block or column ie 1 2, 1 2
    Means same values cannot be in other cells along that row, block or column 
    """
    values, rvalues = [], []
    
    # Search through 9 cell element (row, column or block)
    for e in range(0,9):
        pairs = []
        pair_loc = []
        
        cands = ElemFunc(candBoard, e) 
        
        # Loop through each cell of element see if any pairs (cells with 2 cands)
        for c in range(0,9):
            if len(cands[c]) == 2:
                # Get the values of the pair (a,b) and record location (i,j)
                it = iter(cands[c])
                a,b = next(it), next(it)
                i,j = CoordFunc(e, c)
                
                # If match previously found pair we have a Naked Pair
                for p, pair in enumerate(pairs):
                    i1, j1 = pair_loc[p][0], pair_loc[p][1]
                    if (a,b) == pair:
                        values += [(a,b, i1, j1, i, j)]
                        
                        # Mark candidates with value n in same row/col/block for removal
                        rcells = ElemFunc(board, e)
                        rvalues += RemovalCandidates(rcells, cands, a, lambda k: CoordFunc(e,k), [(i1, j1), (i, j)])
                        rvalues += RemovalCandidates(rcells, cands, b, lambda k: CoordFunc(e,k), [(i1, j1), (i, j)])
                
                # Remember this pair
                pairs += [(a,b)]
                pair_loc += [(i,j)]
            
    return values, rvalues

def NakedPairs(board, candBoard):
    # Rows
    valuesR, rvaluesR = FindNakedPair(board, candBoard, RowCells, lambda b,k: (b,k))
                
    # Columns
    valuesC, rvaluesC = FindNakedPair(board, candBoard, ColCells, lambda b,k: (k,b))
                
    # Blocks
    valuesB, rvaluesB = FindNakedPair(board, candBoard, BlockCells, BlockCoords)
            
    return valuesR + valuesC + valuesB, rvaluesR + rvaluesC + rvaluesB

def FindBoxLinePair(board, candBoard, ElemFunc, isRow):
    """ Finds all box-line pairs in columns or rows.
    Box-line pair is when a particular number can only be in two cells, 
    both of which are in the same block.  Means can eliminate that candidate in 
    that same block in other rows/columns. """
    values, rvalues = [], []
    
    # Search through 9 cell element (row, column or block)
    for e in range(0,9):
        cells = ElemFunc(board, e) 
        candsInElem = ElemFunc(candBoard, e) 
        
        # Loop through all possible numbers
        for n in range(1,10):
            count = 0
            idx = []
            
            # Loop through each cell of the element
            for c in range(0,9):                   
                if cells[c] == 0 and n in candsInElem[c]:
                    count += 1
                    idx += [c]
                                
            # If only found number n twice in col or row, check if in same block
            if count == 2:
                if idx[0]//3 == idx[1]//3:
                    if isRow:
                        i1, j1, i2, j2 = e, idx[0], e, idx[1] 
                    else:
                        i1, j1, i2, j2 = idx[0], e, idx[1], e
                    values += [(n, i1, j1, i2, j2)]
                                        
                    # Mark candidates with value n in same block for removal
                    bi, bj = i1//3,j1//3
                    rcells = BlockCells_coords(board, bi, bj)
                    rcands = BlockCells_coords(candBoard, bi, bj)
                    LocFunc = lambda rc: (3*bi + rc // 3, 3*bj + rc % 3)
                    rvalues += RemovalCandidates(rcells, rcands, n, LocFunc, [(i1, j1), (i2, j2)])
                                        
    return values, rvalues    
    
def BoxLinePairs(board, candBoard):
    valuesR, rvaluesR = FindBoxLinePair(board, candBoard, RowCells, isRow=True)
    valuesC, rvaluesC = FindBoxLinePair(board, candBoard, ColCells, isRow=False)
    
    return valuesR + valuesC, rvaluesR + rvaluesC

def PointingPairs(board, candBoard):
    """ Finds all pointing pairs in either rows or columns.
    Pointing pair is only 2 cells a particular number can go in a block that
    happen to be in same row or column. Means can eliminate that number as 
    candidate in that row/column outside the box."""
    values, rvalues = [], []
    
    # Loop through each block
    for b in range(0,9):
        cellsInBlock = BlockCells(board, b)
        candsInBlock = BlockCells(candBoard, b)
        
        # Loop through all possible numbers
        for n in range(1,10):
            count = 0
            idx = []
            
            # Loop through each cell of the block
            for c in range(0,9):
                if cellsInBlock[c] == 0 and n in candsInBlock[c]:
                    count += 1
                    idx += [c]

            # If only found number n twice in col or row, check if in same row/col
            if count == 2:
                i1,j1 = BlockCoords(b,idx[0])
                i2,j2 = BlockCoords(b,idx[1])
                
                if i1 == i2 or j1 == j2: 
                    values += [(n, i1, j1, i2, j2)]
                    
                    # Mark candidates with value n in same row/col for removal
                    rcells = RowCells(board, i1) if i1 == i2 else ColCells(board, j1)
                    rcands = RowCells(candBoard, i1) if i1 == i2 else ColCells(candBoard, j1)
                    LocFunc = lambda rc: (i1, rc) if i1 == i2 else (rc, j1)
                    rvalues += RemovalCandidates(rcells, rcands, n, LocFunc, [(i1, j1), (i2, j2)])
                    
    return values, rvalues 

def FindBoxTriples(board, candBoard, ElemFunc, CoordFunc):
    values, rvalues = [], []
    
    # For each row/col
    for e in range(0,9):
        cells = ElemFunc(board, e)      # Cells in this row or column only
        cands = ElemFunc(candBoard, e)  # Cands in this row or column only
        
        # Loop thro each set of 3 cells in each block in this row/col
        for b in range(0,3):
            tripCandSet = set()            
            bs = 3*b
            bf = bs + 3
            
            # If no cells filled in for this row/col in this block 
            if cells[bs:bf] == [0,0,0]:
                for c in range(0,3):
                    tripCandSet |=  cands[bs + c]
                    
                # If only 3 possible candidates in these 3 cells
                if len(tripCandSet) == 3:
                    trip_loc = [CoordFunc(e, bs + k) for k in range(0,3)]
                    x, y, z = tripCandSet
                    values += [tuple(tripCandSet)+tuple(trip_loc)]
                             
                    # Mark candidates with value n in same row/col for removal
                    rcells = ElemFunc(board, e)
                    rvalues += RemovalCandidates(rcells, cands, x, lambda k: CoordFunc(e,k), trip_loc)
                    rvalues += RemovalCandidates(rcells, cands, y, lambda k: CoordFunc(e,k), trip_loc)
                    rvalues += RemovalCandidates(rcells, cands, z, lambda k: CoordFunc(e,k), trip_loc)                       

                    # Mark candidates with value n in same block for removal
                    bi, bj = trip_loc[0][0]//3, trip_loc[0][1]//3 
                    rbcells = BlockCells_coords(board, bi, bj)
                    rbcands = BlockCells_coords(candBoard, bi, bj)
                    rvalues += RemovalCandidates(rbcells, rbcands, x, lambda k: BlockCoords_coords(bi, bj, k), trip_loc)
                    rvalues += RemovalCandidates(rbcells, rbcands, y, lambda k: BlockCoords_coords(bi, bj, k), trip_loc)
                    rvalues += RemovalCandidates(rbcells, rbcands, z, lambda k: BlockCoords_coords(bi, bj, k), trip_loc)                       
                        
    return values, rvalues                 
                 
def BoxTriples(board, candBoard):
    # Rows
    valuesR, rvaluesR = FindBoxTriples(board, candBoard, RowCells, lambda b,k: (b,k))
    # Columns 
    valuesC, rvaluesC = FindBoxTriples(board, candBoard, ColCells, lambda b,k: (k,b)) 
    
    return valuesR + valuesC, rvaluesR + rvaluesC

def FindXWing(board, candBoard, ElemFunc, CoordFunc):
    values = []
    
    # Loop through all possible numbers
    for n in range(1,10):
        
        pair_loc = []

        # For each row/col
        for e in range(0,9):
            cells = ElemFunc(board, e)      # Cells in this row or column only
            cands = ElemFunc(candBoard, e)  # Cands in this row or column only
    
            count = 0
            idx = []
            
            # Loop through each cell of the element
            for c in range(0,9):                   
                if cells[c] == 0 and n in cands[c]:
                    count += 1
                    idx += [c]
                    
            if count == 2:
                for pair in pair_loc:
                    ep, idxp = pair
                    if idxp == idx:
                        values += [(n, CoordFunc(e, idx[0]), CoordFunc(e, idx[1]), CoordFunc(ep, idxp[0]), CoordFunc(ep, idxp[1]))]
                pair_loc += [(e, idx)]

    return values

def XWingRemovals(board, candBoard, xwings):
    rvalues = []
    for xwing in xwings:
        n, (i1,j1),(i2,j2),(i3,j3),(i4,j4) = xwing
        
        rows = list(set([i1, i2, i3, i4]))
        cols = list(set([j1, j2, j3, j4]))
        
        for row in rows:
            rowCells = RowCells(board, row)
            rowCands = RowCells(candBoard, row)
        
            for col in range(0,9):
                if col not in cols and rowCells[col] == 0 and n in rowCands[col]:
                    rvalues += [(n, row, col)]

        for col in cols:
            colCells = ColCells(board, col)
            colCands = ColCells(candBoard, col)
        
            for row in range(0,9):
                if row not in rows and colCells[row] == 0 and n in colCands[row]:
                    rvalues += [(n, row, col)]

    return rvalues
                
def XWings(board, candBoard):
    # Rows
    valuesR = FindXWing(board, candBoard, RowCells, lambda b,k: (b,k))
    # Columns 
    valuesC = FindXWing(board, candBoard, ColCells, lambda b,k: (k,b))
    
    values = valuesR + valuesC
    
    rvalues = XWingRemovals(board, candBoard, values)
    
    return values, rvalues
    
      
def RemovalCandidates(cells, cands, n, LocFunc, exclList):
    """ List the candidates to be marked for removal.  Based on a function 
    LocFunc that translates the 0->9 value of rc to i,j cell coords, the 
    number n to be removed and a list of cells excluded from removal.  The 
    latter exclusion is for the cells that cause the removal (ie orig pointing
    pair or similar) to avoid candidates causing their own removal.
    """
    rvalues = []
    
    # Loop through each cell of the block
    for rc in range(0,9):
        ri,rj = LocFunc(rc)
        
        if cells[rc] == 0 and n in cands[rc]:
            if (ri,rj) not in exclList:
                rvalues += [(n, ri, rj)]
    
    return rvalues
                

