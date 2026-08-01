"""Sudoku generation and validation helpers."""

import copy
import random

SIZE = 9
EMPTY = 0
DIFFICULTY_SETTINGS = {
    "easy": 40,
    "medium": 32,
    "hard": 28,
}


def deep_copy(board):
    """Return a deep copy of a Sudoku board."""
    return copy.deepcopy(board)


def create_empty_board():
    """Create a Sudoku board filled with empty cells."""
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    """Return True when placing num at the given position is valid."""
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False

    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def fill_board(board):
    """Recursively fill a board with a valid Sudoku solution."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def remove_cells(board, clues):
    """Remove cells from a completed board until it has the requested clues."""
    attempts = SIZE * SIZE - clues
    while attempts > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            attempts -= 1


def find_empty_cell(board):
    """Return the next empty cell coordinates or None when solved."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col
    return None


def count_solutions(board, limit=2):
    """Count solutions for the current board up to the specified limit."""
    empty_cell = find_empty_cell(board)
    if empty_cell is None:
        return 1

    row, col = empty_cell
    solutions = 0
    for candidate in range(1, SIZE + 1):
        if not is_safe(board, row, col, candidate):
            continue
        board[row][col] = candidate
        solutions += count_solutions(board, limit)
        board[row][col] = EMPTY
        if solutions >= limit:
            return limit
    return solutions


def find_incorrect_positions(board, solution):
    """Return the coordinates that differ from the provided solution."""
    incorrect = []
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                continue
            if board[row][col] != solution[row][col]:
                incorrect.append([row, col])
    return incorrect


def is_board_solved(board, solution):
    """Return True when the board is complete and exactly matches the solution."""
    if board is None or solution is None:
        return False

    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return False
            if board[row][col] != solution[row][col]:
                return False
    return True


def resolve_clue_count(clues=35, difficulty=None):
    """Resolve the requested clue count from a legacy clue value or difficulty."""
    if difficulty is not None:
        difficulty_key = difficulty.lower()
        if difficulty_key in DIFFICULTY_SETTINGS:
            return DIFFICULTY_SETTINGS[difficulty_key]

    if clues is None:
        return 35
    return clues


def generate_puzzle(clues=35, difficulty=None):
    """Generate a puzzle and its matching solution."""
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)

    target_clues = resolve_clue_count(clues, difficulty)
    puzzle = deep_copy(solution)
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)

    while sum(cell != EMPTY for row in puzzle for cell in row) > target_clues:
        removed = False
        for row, col in cells:
            if puzzle[row][col] == EMPTY:
                continue
            value = puzzle[row][col]
            puzzle[row][col] = EMPTY
            if count_solutions(deep_copy(puzzle)) == 1:
                removed = True
                break
            puzzle[row][col] = value

        if not removed:
            break

    return puzzle, solution
