"""Flask application for the Sudoku game."""

from flask import Flask, jsonify, render_template, request

import sudoku_logic

# Keep a simple in-memory store for current puzzle and solution.
CURRENT = {
    "puzzle": None,
    "solution": None,
}


def create_app():
    """Create and configure the Flask application instance."""
    app = Flask(__name__)
    app.add_url_rule("/", view_func=index)
    app.add_url_rule("/new", view_func=new_game)
    app.add_url_rule("/check", view_func=check_solution, methods=["POST"])
    app.add_url_rule("/hint", view_func=hint, methods=["POST"])
    return app


def index():
    """Render the main game page."""
    return render_template("index.html")


def new_game():
    """Generate a new puzzle and store it in the current game state."""
    clues = request.args.get("clues")
    difficulty = request.args.get("difficulty")
    clues_value = int(clues) if clues is not None else None
    puzzle, solution = sudoku_logic.generate_puzzle(clues=clues_value, difficulty=difficulty)
    CURRENT["puzzle"] = puzzle
    CURRENT["solution"] = solution
    return jsonify({"puzzle": puzzle, "solution": solution})


def check_solution():
    """Return the positions that do not match the current solution."""
    board = request.json.get("board")
    solution = CURRENT.get("solution")
    if solution is None:
        return jsonify({"error": "No game in progress"}), 400

    incorrect = sudoku_logic.find_incorrect_positions(board, solution)
    solved = sudoku_logic.is_board_solved(board, solution)
    return jsonify({"incorrect": incorrect, "solved": solved})


def hint():
    """Fill one empty cell with the correct value from the stored solution."""
    board = request.json.get("board")
    solution = CURRENT.get("solution")
    if solution is None:
        return jsonify({"error": "No game in progress"}), 400

    updated_board = [row[:] for row in board]
    for row in range(len(updated_board)):
        for col in range(len(updated_board[row])):
            if updated_board[row][col] == 0:
                updated_board[row][col] = solution[row][col]
                return jsonify({
                    "row": row,
                    "col": col,
                    "value": solution[row][col],
                    "board": updated_board,
                })

    return jsonify({"error": "No empty cells left"}), 400


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)