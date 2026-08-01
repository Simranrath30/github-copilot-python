// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_STORAGE_KEY = 'sudoku-top10-leaderboard';
const THEME_STORAGE_KEY = 'sudoku-theme';
let puzzle = [];
let currentBoard = [];
let lockedCells = new Set();
let solution = [];
let completionMessageShown = false;
let completionEntryRecorded = false;
let timerInterval = null;
let elapsedSeconds = 0;
let leaderboardEntries = [];

function updateTimerDisplay() {
  const timer = document.getElementById('timer');
  if (!timer) return;
  const minutes = String(Math.floor(elapsedSeconds / 60)).padStart(2, '0');
  const seconds = String(elapsedSeconds % 60).padStart(2, '0');
  timer.innerText = `${minutes}:${seconds}`;
}

function formatTime(totalSeconds) {
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
  const seconds = String(totalSeconds % 60).padStart(2, '0');
  return `${minutes}:${seconds}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function setCellAppearance(input, { isLocked = false, isIncorrect = false } = {}) {
  const blockClass = input.classList.contains('block-even') ? 'block-even' : 'block-odd';
  const classes = ['sudoku-cell', blockClass];

  if (isLocked) {
    classes.push('prefilled');
  }

  if (isIncorrect) {
    classes.push('incorrect');
  }

  input.className = classes.join(' ');
}

function loadLeaderboard() {
  const savedEntries = window.localStorage.getItem(LEADERBOARD_STORAGE_KEY);
  if (!savedEntries) {
    leaderboardEntries = [];
    renderLeaderboard();
    return;
  }

  try {
    leaderboardEntries = JSON.parse(savedEntries);
  } catch (error) {
    leaderboardEntries = [];
  }
  renderLeaderboard();
}

function saveLeaderboard() {
  window.localStorage.setItem(LEADERBOARD_STORAGE_KEY, JSON.stringify(leaderboardEntries));
}

function renderLeaderboard() {
  const leaderboard = document.getElementById('leaderboard-list');
  if (!leaderboard) return;

  if (leaderboardEntries.length === 0) {
    leaderboard.innerHTML = '<li class="leaderboard-empty">No completed games yet.</li>';
    return;
  }

  leaderboard.innerHTML = leaderboardEntries
    .map((entry, index) => {
      const rank = index + 1;
      const formattedTime = formatTime(entry.timeSeconds);
      return `
        <li class="leaderboard-item">
          <span class="leaderboard-rank">#${rank}</span>
          <span class="leaderboard-name">${escapeHtml(entry.name)}</span>
          <span class="leaderboard-time">${formattedTime}</span>
          <span class="leaderboard-difficulty">${escapeHtml(entry.difficulty)}</span>
        </li>`;
    })
    .join('');
}

function recordCompletion() {
  if (completionEntryRecorded || solution.length === 0) {
    return;
  }

  const playerNameInput = document.getElementById('player-name');
  const name = playerNameInput && playerNameInput.value.trim()
    ? playerNameInput.value.trim()
    : 'Anonymous';
  const difficulty = document.getElementById('difficulty').value;
  const entry = {
    name,
    timeSeconds: elapsedSeconds,
    difficulty,
    completedAt: new Date().toISOString(),
  };

  leaderboardEntries.push(entry);
  leaderboardEntries.sort((left, right) => {
    if (left.timeSeconds !== right.timeSeconds) {
      return left.timeSeconds - right.timeSeconds;
    }
    return left.completedAt.localeCompare(right.completedAt);
  });
  leaderboardEntries = leaderboardEntries.slice(0, 10);
  saveLeaderboard();
  renderLeaderboard();
  completionEntryRecorded = true;
}

function stopTimer() {
  if (timerInterval !== null) {
    window.clearInterval(timerInterval);
    timerInterval = null;
  }
}

function startTimer() {
  stopTimer();
  elapsedSeconds = 0;
  updateTimerDisplay();
  timerInterval = window.setInterval(() => {
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function applyTheme(theme) {
  const isDarkMode = theme === 'dark';
  document.body.classList.toggle('theme-dark', isDarkMode);
  const toggleButton = document.getElementById('theme-toggle');
  if (toggleButton) {
    toggleButton.textContent = isDarkMode ? 'Light Mode' : 'Dark Mode';
    toggleButton.setAttribute('aria-pressed', String(isDarkMode));
  }
}

function loadTheme() {
  const savedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
  if (savedTheme === 'dark' || savedTheme === 'light') {
    applyTheme(savedTheme);
    return;
  }

  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  applyTheme(prefersDark ? 'dark' : 'light');
}

function toggleTheme() {
  const nextTheme = document.body.classList.contains('theme-dark') ? 'light' : 'dark';
  applyTheme(nextTheme);
  window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
}

function showCompletionMessage() {
  if (completionMessageShown) {
    return;
  }
  const msg = document.getElementById('message');
  msg.style.color = 'var(--message-success)';
  msg.innerText = 'Congratulations! You solved it!';
  completionMessageShown = true;
  stopTimer();
  recordCompletion();
}

function updateCompletionState() {
  if (solution.length === 0) {
    completionMessageShown = false;
    return false;
  }

  let solved = true;
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      if (currentBoard[i][j] === 0 || currentBoard[i][j] !== solution[i][j]) {
        solved = false;
        break;
      }
    }
    if (!solved) break;
  }

  if (solved) {
    showCompletionMessage();
    return true;
  }

  if (completionMessageShown) {
    const msg = document.getElementById('message');
    msg.innerText = '';
    completionMessageShown = false;
  }
  return false;
}

function applyCellHighlighting(incorrectPositions) {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const incorrectSet = new Set(incorrectPositions.map(([row, col]) => row * SIZE + col));

  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.readOnly) continue;

    setCellAppearance(inp, { isLocked: false, isIncorrect: incorrectSet.has(idx) });
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      const blockIndex = Math.floor(i / 3) * 3 + Math.floor(j / 3);
      const blockVariant = blockIndex % 2 === 0 ? 'block-even' : 'block-odd';
      input.className = `sudoku-cell ${blockVariant}`;
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        const row = parseInt(e.target.dataset.row, 10);
        const col = parseInt(e.target.dataset.col, 10);
        currentBoard[row][col] = val ? parseInt(val, 10) : 0;

        if (solution.length > 0 && currentBoard[row][col] !== 0) {
          const isCorrect = currentBoard[row][col] === solution[row][col];
          setCellAppearance(e.target, { isLocked: false, isIncorrect: !isCorrect });
        } else {
          setCellAppearance(e.target, { isLocked: false, isIncorrect: false });
        }
        updateCompletionState();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderBoardView() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = currentBoard[i][j];
      const inp = inputs[idx];
      const cellKey = `${i}-${j}`;
      const isLocked = lockedCells.has(cellKey) || val !== 0;
      if (isLocked) {
        inp.value = val;
        inp.readOnly = true;
        setCellAppearance(inp, { isLocked: true, isIncorrect: false });
      } else {
        inp.value = '';
        inp.readOnly = false;
        setCellAppearance(inp, { isLocked: false, isIncorrect: false });
      }
    }
  }
}

function renderPuzzle(puz, sol = []) {
  puzzle = puz;
  currentBoard = puz.map((row) => row.slice());
  solution = sol;
  lockedCells = new Set();
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      if (currentBoard[i][j] !== 0) {
        lockedCells.add(`${i}-${j}`);
      }
    }
  }
  createBoardElement();
  renderBoardView();
  completionMessageShown = false;
  completionEntryRecorded = false;
  startTimer();
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  renderPuzzle(data.puzzle, data.solution || []);
  document.getElementById('message').innerText = '';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  currentBoard = board;
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = 'var(--message-error)';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  applyCellHighlighting(data.incorrect);
  if (data.solved) {
    showCompletionMessage();
  } else {
    msg.style.color = 'var(--message-error)';
    msg.innerText = 'Some cells are incorrect.';
    completionMessageShown = false;
  }
}

async function applyHint() {
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board: currentBoard})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = 'var(--message-error)';
    msg.innerText = data.error;
    return;
  }
  currentBoard = data.board;
  lockedCells.add(`${data.row}-${data.col}`);
  renderBoardView();
  updateCompletionState();
  if (!completionMessageShown) {
    msg.style.color = 'var(--message-info)';
    msg.innerText = 'Hint used.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  loadTheme();
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', applyHint);
  document.getElementById('difficulty').addEventListener('change', newGame);
  loadLeaderboard();
  newGame();
});