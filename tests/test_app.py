import app as app_module


def _make_solution_board():
    return [
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


def test_index_route_renders_page():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        response = client.get("/")

    assert response.status_code == 200
    assert b"Sudoku Game" in response.data


def test_new_game_route_returns_a_puzzle():
    app_module.CURRENT["puzzle"] = None
    app_module.CURRENT["solution"] = None
    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as client:
        response = client.get("/new?clues=40")

    assert response.status_code == 200
    payload = response.get_json()
    assert "puzzle" in payload
    assert len(payload["puzzle"]) == 9
    assert app_module.CURRENT["puzzle"] is not None
    assert app_module.CURRENT["solution"] is not None


def test_new_game_route_uses_difficulty_to_control_clue_count():
    app_module.CURRENT["puzzle"] = None
    app_module.CURRENT["solution"] = None
    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as client:
        easy_response = client.get("/new?difficulty=easy")
        medium_response = client.get("/new?difficulty=medium")
        hard_response = client.get("/new?difficulty=hard")

    easy_clues = sum(cell != 0 for row in easy_response.get_json()["puzzle"] for cell in row)
    medium_clues = sum(cell != 0 for row in medium_response.get_json()["puzzle"] for cell in row)
    hard_clues = sum(cell != 0 for row in hard_response.get_json()["puzzle"] for cell in row)

    assert easy_clues > medium_clues
    assert medium_clues > hard_clues


def test_check_solution_reports_incorrect_positions():
    solution = _make_solution_board()
    board = [row[:] for row in solution]
    board[0][0] = 2

    app_module.CURRENT["solution"] = solution
    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as client:
        response = client.post("/check", json={"board": board})

    assert response.status_code == 200
    assert response.get_json()["incorrect"] == [[0, 0]]
    assert response.get_json()["solved"] is False


def test_check_solution_marks_completed_when_the_board_is_full_and_correct():
    solution = _make_solution_board()
    board = [row[:] for row in solution]

    app_module.CURRENT["solution"] = solution
    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as client:
        response = client.post("/check", json={"board": board})

    assert response.status_code == 200
    assert response.get_json()["incorrect"] == []
    assert response.get_json()["solved"] is True


def test_check_solution_returns_error_when_no_game_is_active():
    app_module.CURRENT["solution"] = None
    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as client:
        response = client.post("/check", json={"board": _make_solution_board()})

    assert response.status_code == 400
    assert response.get_json()["error"] == "No game in progress"


def test_hint_route_returns_one_correct_value_from_the_stored_solution():
    solution = _make_solution_board()
    board = [row[:] for row in solution]
    board[0][0] = 0

    app_module.CURRENT["solution"] = solution
    app_module.CURRENT["puzzle"] = board
    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as client:
        response = client.post("/hint", json={"board": board})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["row"] == 0
    assert payload["col"] == 0
    assert payload["value"] == 1
    assert payload["board"][0][0] == 1


def test_index_route_includes_leaderboard_section():
    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as client:
        response = client.get("/")

    assert response.status_code == 200
    assert b'id="leaderboard"' in response.data
    assert b"Top 10 Leaderboard" in response.data


def test_index_route_includes_theme_toggle_button():
    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as client:
        response = client.get("/")

    assert response.status_code == 200
    assert b'id="theme-toggle"' in response.data
    assert b"Dark Mode" in response.data
