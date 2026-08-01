import sudoku_logic


def _is_valid_sudoku_board(board):
    expected = set(range(1, sudoku_logic.SIZE + 1))

    for row in board:
        if set(row) != expected:
            return False

    for col in range(sudoku_logic.SIZE):
        if {board[row][col] for row in range(sudoku_logic.SIZE)} != expected:
            return False

    for start_row in range(0, sudoku_logic.SIZE, 3):
        for start_col in range(0, sudoku_logic.SIZE, 3):
            values = {
                board[r][c]
                for r in range(start_row, start_row + 3)
                for c in range(start_col, start_col + 3)
            }
            if values != expected:
                return False

    return True


def test_create_empty_board_has_expected_structure():
    board = sudoku_logic.create_empty_board()
    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_is_safe_detects_row_column_and_box_conflicts():
    board = sudoku_logic.create_empty_board()
    assert sudoku_logic.is_safe(board, 0, 0, 1)

    board[0][0] = 1
    assert not sudoku_logic.is_safe(board, 0, 1, 1)
    assert not sudoku_logic.is_safe(board, 1, 0, 1)


def test_fill_board_creates_valid_solution():
    board = sudoku_logic.create_empty_board()
    assert sudoku_logic.fill_board(board)
    assert _is_valid_sudoku_board(board)


def test_generate_puzzle_returns_puzzle_and_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert _is_valid_sudoku_board(solution)
    assert any(cell == sudoku_logic.EMPTY for row in puzzle for cell in row)
    assert all(0 <= cell <= sudoku_logic.SIZE for row in puzzle for cell in row)


def test_generate_puzzle_respects_difficulty_levels():
    easy_puzzle, _ = sudoku_logic.generate_puzzle(difficulty="easy")
    medium_puzzle, _ = sudoku_logic.generate_puzzle(difficulty="medium")
    hard_puzzle, _ = sudoku_logic.generate_puzzle(difficulty="hard")

    easy_clues = sum(cell != sudoku_logic.EMPTY for row in easy_puzzle for cell in row)
    medium_clues = sum(cell != sudoku_logic.EMPTY for row in medium_puzzle for cell in row)
    hard_clues = sum(cell != sudoku_logic.EMPTY for row in hard_puzzle for cell in row)

    assert easy_clues > medium_clues
    assert medium_clues > hard_clues


def test_find_incorrect_positions_ignores_empty_cells_and_only_flags_wrong_entries():
    solution = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
    ]
    board = [row[:] for row in solution]
    board[0][0] = sudoku_logic.EMPTY
    board[0][1] = 3
    board[0][2] = 2

    assert sudoku_logic.find_incorrect_positions(board, solution) == [[0, 1], [0, 2]]


def test_is_board_solved_requires_a_full_and_correct_board():
    solution = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
    ]
    completed_board = [row[:] for row in solution]
    assert sudoku_logic.is_board_solved(completed_board, solution)

    incorrect_board = [row[:] for row in solution]
    incorrect_board[0][0] = 2
    assert not sudoku_logic.is_board_solved(incorrect_board, solution)

    incomplete_board = [row[:] for row in solution]
    incomplete_board[0][0] = sudoku_logic.EMPTY
    assert not sudoku_logic.is_board_solved(incomplete_board, solution)
