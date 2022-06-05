import sudoku as sd
import pytest


@pytest.fixture
def test_board():
    board = [
        [7, 8, 0, 4, 0, 0, 1, 2, 0],
        [6, 0, 0, 0, 7, 5, 0, 0, 9],
        [0, 0, 0, 6, 0, 1, 0, 7, 8],
        [0, 0, 7, 0, 4, 0, 2, 6, 0],
        [0, 0, 1, 0, 5, 0, 9, 3, 0],
        [9, 0, 4, 0, 6, 0, 0, 0, 5],
        [0, 7, 0, 3, 0, 0, 0, 1, 2],
        [1, 2, 0, 0, 0, 7, 4, 0, 0],
        [0, 4, 9, 2, 0, 6, 0, 0, 7]
    ]
    return board


def test_single_solution(test_board):
    ns, sb = sd.SolvewBacktrack(test_board)
    assert ns == 1


def test_row_duplicate(test_board):
    test_board[4][4] = 3
    assert sd.BoardIsValid(test_board) is False


def test_column_duplicate(test_board):
    test_board[4][4] = 7
    assert sd.BoardIsValid(test_board) is False


def test_block_duplicate(test_board):
    test_board[4][4] = 5
    test_board[8][8] = 1
    assert sd.BoardIsValid(test_board) is False


def test_no_solutions_invalid_board(test_board):
    test_board[4][4] = 5
    test_board[8][8] = 1
    ns, sb = sd.SolvewBacktrack(test_board)
    assert ns == 0


def test_multiple_solutions():
    test_board2 = [
        [7, 8, 0, 4, 0, 0, 1, 2, 0],
        [6, 0, 0, 0, 7, 5, 0, 0, 9],
        [0, 0, 0, 6, 0, 1, 0, 7, 8],
        [0, 0, 7, 0, 4, 0, 2, 6, 0],
        [0, 0, 1, 0, 5, 0, 9, 3, 0],
        [9, 0, 4, 0, 6, 0, 0, 0, 5],
        [0, 7, 0, 3, 0, 0, 0, 1, 2],
        [1, 2, 0, 0, 0, 0, 4, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    ns, sb = sd.SolvewBacktrack(test_board2)
    assert ns > 1
