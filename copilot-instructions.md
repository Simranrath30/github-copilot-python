# Copilot Instructions for the Flask Sudoku Project

## Project overview
This repository contains a small Flask web app for playing Sudoku. The app has three main parts:
- Flask routes and request handling in app.py
- Sudoku game logic in sudoku_logic.py
- Frontend rendering and interaction in static/main.js and templates/index.html

## General coding guidelines
- Follow PEP 8 style consistently.
- Use descriptive names for functions, variables, and constants.
- Keep code modular and maintainable by separating concerns.
- Add docstrings to functions and modules where appropriate.
- Preserve existing functionality unless the task explicitly requires a change.
- Prefer small, focused functions over large monolithic blocks of code.
- Keep imports organized and avoid unused code.

## Flask-specific guidance
- Keep Flask routes lightweight.
- Route handlers should mainly parse input, call a service or helper function, and return a response.
- Avoid putting complex game logic directly inside route functions.
- Keep application state and business logic in separate modules where possible.
- Preserve the existing API behavior for endpoints such as /new and /check.

## Sudoku-specific guidance
- Keep Sudoku validation and generation logic in sudoku_logic.py whenever possible.
- Preserve the current rules of Sudoku: rows, columns, and 3x3 boxes must all contain unique values.
- Use clear and readable logic for board generation, validation, and puzzle creation.
- Avoid introducing unnecessary randomness or behavior changes that would alter the game experience.

## Testing guidance
- Use pytest for all new or updated tests.
- Write tests for core logic such as board validation, puzzle generation, and route behavior.
- Prefer simple, readable test cases that verify behavior clearly.
- When changing existing functionality, add or update tests to protect the current behavior.

## Maintainability guidance
- Favor readability over cleverness.
- Keep functions focused on a single responsibility.
- Use constants for fixed values such as board size and empty-cell markers.
- When adding new features, try to fit them into the existing structure rather than introducing new patterns unnecessarily.

## Preferred approach for changes
- Understand the current behavior before editing it.
- Make minimal, targeted changes.
- Preserve the current user experience unless a feature request requires otherwise.
- If a change affects the frontend, ensure the Flask API contract remains compatible.

## Project Feature Requirements

- Preserve the existing Sudoku gameplay unless a feature explicitly requires a change.
- Every generated Sudoku puzzle must have exactly one unique solution.
- Keep the UI responsive on desktop and mobile devices.
- Support both light and dark mode.
- Use browser localStorage for persistent client-side data such as the Top 10 leaderboard and theme preference.
- Keep frontend JavaScript modular and avoid unnecessary global variables.
- Ensure Hint, Check, Timer, Difficulty Selector, and Leaderboard features integrate cleanly with the existing application.

## Testing Workflow

- Run pytest after every significant code change.
- Do not remove or weaken existing tests.
- When implementing new functionality, add or update tests where appropriate.
- Keep the application in a passing state before moving to the next feature.

## Copilot Expectations

- Explain major code changes before applying them.
- Prefer incremental changes over large rewrites.
- Preserve backward compatibility whenever possible.
- If multiple implementation approaches exist, recommend the simplest maintainable solution first.