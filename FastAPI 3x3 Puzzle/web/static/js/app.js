const state = {
  difficulty: "easy",
  size: 3,
  tiles: [],
  moves: 0,
  timerId: null,
  startedAt: null,
  elapsedSeconds: 0,
  completed: false,
  loading: false,
  loadRequestId: 0,
  puzzleAbortController: null,
  facts: [],
  factIndex: 0,
  factTimerId: null,
  factCountdownId: null,
  factStartedAt: null,
  drag: null,
  audioContext: null,
  lastInvalidSoundAt: 0,
  lastCelebrationSoundAt: 0,
  completionCount: 0,
  confettiCleanupId: null,
  completionSaveId: 0,
  solverPlaybackStates: [],
  solverPlaybackMoves: [],
  solverPlaybackIndex: 0,
};

const FACT_ROTATION_MS = 30000;
const FACT_COUNTDOWN_MS = 250;
const CELEBRATION_SOUND_COOLDOWN_MS = 1600;
const invalidFeedbackTimers = new WeakMap();
const CONFETTI_COLORS = ["#73ffb8", "#ffe066", "#ff78c4", "#7dd3ff", "#bc8cff", "#ff8a5b"];

const boardEl = document.querySelector("#puzzle-board");
const movesEl = document.querySelector("#moves-count");
const timeEl = document.querySelector("#time-count");
const factEl = document.querySelector("#fact-text");
const factCountdownBarEl = document.querySelector("#fact-countdown-bar");
const confettiLayerEl = document.querySelector("#confetti-layer");
const successMessageEl = document.querySelector("#success-message");
const usernameInput = document.querySelector("#username-input");
const usernameDisplay = document.querySelector("#username-display");
const saveUsernameButton = document.querySelector("#save-username");
const newPuzzleButton = document.querySelector("#new-puzzle");
const difficultyButtons = document.querySelectorAll(".difficulty-button");
const solverResultsEl = document.querySelector("#solver-results");
const solverStartBoardEl = document.querySelector("#solver-start-board");
const solverComparisonBodyEl = document.querySelector("#solver-comparison-body");
const solverPlaybackBoardEl = document.querySelector("#solver-playback-board");
const solverStepLabelEl = document.querySelector("#solver-step-label");
const solverPlaybackMoveEl = document.querySelector("#solver-playback-move");
const solverPrevStepButton = document.querySelector("#solver-prev-step");
const solverNextStepButton = document.querySelector("#solver-next-step");
const solverResetStepButton = document.querySelector("#solver-reset-step");

function formatTime(seconds) {
  return `${seconds}s`;
}

function currentElapsedSeconds() {
  if (state.startedAt === null) {
    return state.elapsedSeconds;
  }
  return Math.floor((Date.now() - state.startedAt) / 1000);
}

function updateTimerDisplay(seconds = state.elapsedSeconds) {
  state.elapsedSeconds = seconds;
  timeEl.textContent = formatTime(seconds);
}

function stopTimer({ preserveElapsed = true } = {}) {
  if (preserveElapsed && state.startedAt !== null) {
    updateTimerDisplay(currentElapsedSeconds());
  }
  if (state.timerId !== null) {
    clearInterval(state.timerId);
    state.timerId = null;
  }
  state.startedAt = null;
}

function startTimer() {
  stopTimer({ preserveElapsed: false });
  state.elapsedSeconds = 0;
  state.startedAt = Date.now();
  updateTimerDisplay(0);
  state.timerId = window.setInterval(() => {
    if (state.completed) {
      stopTimer();
      return;
    }
    updateTimerDisplay(currentElapsedSeconds());
  }, 500);
}

function updateMetrics() {
  movesEl.textContent = String(state.moves);
}

function clearCelebration() {
  if (state.confettiCleanupId !== null) {
    clearTimeout(state.confettiCleanupId);
    state.confettiCleanupId = null;
  }
  confettiLayerEl.innerHTML = "";
  boardEl.classList.remove("solved");
  boardEl.dataset.completed = "false";
  boardEl.dataset.completionSaved = "false";
  delete boardEl.dataset.completionRecordId;
  successMessageEl.hidden = true;
  successMessageEl.innerHTML = "";
}

function setGameLoading(isLoading) {
  state.loading = isLoading;
  boardEl.setAttribute("aria-busy", String(isLoading));
  newPuzzleButton.disabled = isLoading;
  difficultyButtons.forEach((button) => {
    button.disabled = isLoading;
  });
}

function completePuzzle() {
  if (state.completed) {
    return;
  }
  state.completed = true;
  stopTimer({ preserveElapsed: true });
  state.completionCount += 1;
  boardEl.dataset.completed = "true";
  boardEl.dataset.completionCount = String(state.completionCount);
  boardEl.classList.add("solved");
  boardEl.setAttribute("aria-label", "Puzzle solved");
  successMessageEl.hidden = false;
  successMessageEl.innerHTML = `
    <strong>Completed</strong>
    <span>${formatTime(state.elapsedSeconds)} - ${state.moves} moves</span>
    <small id="completion-save-status"></small>
  `;
  launchConfetti();
  playCelebrationSound();
  void saveCompletionRecord();
}

function resetGameSession(payload) {
  stopTimer({ preserveElapsed: false });
  state.drag = null;
  clearCelebration();
  state.difficulty = payload.difficulty_key;
  state.size = payload.state.size;
  state.tiles = payload.state.tiles;
  state.moves = 0;
  state.elapsedSeconds = 0;
  state.completed = false;
  state.completionSaveId += 1;
  updateMetrics();
  updateTimerDisplay(0);
  renderBoard();
  boardEl.setAttribute(
    "aria-label",
    `${payload.difficulty} ${payload.dimensions} sliding puzzle board`
  );
  setDifficultyButton(state.difficulty);
  startTimer();
}

function goalTiles(size) {
  const tiles = [];
  for (let value = 1; value < size * size; value += 1) {
    tiles.push(value);
  }
  tiles.push(0);
  return tiles;
}

function isGoal() {
  const goal = goalTiles(state.size);
  return state.tiles.every((tile, index) => tile === goal[index]);
}

function rowCol(index) {
  return {
    row: Math.floor(index / state.size),
    column: index % state.size,
  };
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function interactionId(event) {
  return event.pointerId ?? (event.type.startsWith("touch") ? "touch" : "mouse");
}

function interactionPoint(event) {
  const touch = event.changedTouches?.[0] || event.touches?.[0];
  if (touch) {
    return {
      x: touch.clientX,
      y: touch.clientY,
    };
  }
  return {
    x: event.clientX,
    y: event.clientY,
  };
}

function blankMoveForTile(tileIndex) {
  const blankIndex = state.tiles.indexOf(0);
  const tilePos = rowCol(tileIndex);
  const blankPos = rowCol(blankIndex);
  const rowDelta = tilePos.row - blankPos.row;
  const columnDelta = tilePos.column - blankPos.column;

  if (Math.abs(rowDelta) + Math.abs(columnDelta) !== 1) {
    return null;
  }
  if (rowDelta === -1) return "UP";
  if (rowDelta === 1) return "DOWN";
  if (columnDelta === -1) return "LEFT";
  if (columnDelta === 1) return "RIGHT";
  return null;
}

function blankAdjacencyForTile(tileIndex) {
  const blankIndex = state.tiles.indexOf(0);
  const tilePos = rowCol(tileIndex);
  const blankPos = rowCol(blankIndex);
  const rowDelta = blankPos.row - tilePos.row;
  const columnDelta = blankPos.column - tilePos.column;
  const move = blankMoveForTile(tileIndex);

  if (!move) {
    return null;
  }
  return {
    blankIndex,
    move,
    rowDelta,
    columnDelta,
  };
}

function tileCenter(element) {
  const rect = element.getBoundingClientRect();
  return {
    x: rect.left + rect.width / 2,
    y: rect.top + rect.height / 2,
  };
}

function dragTargetOffset(tileIndex, tileElement) {
  const blankElement = boardEl.querySelector(".tile.blank");
  const tile = tileCenter(tileElement);
  const blank = tileCenter(blankElement);
  return {
    x: blank.x - tile.x,
    y: blank.y - tile.y,
  };
}

function dispatchInvalidMove(tileIndex, reason) {
  const event = new CustomEvent("puzzle:invalid-move", {
    detail: {
      tileIndex,
      tile: state.tiles[tileIndex],
      reason,
    },
  });
  boardEl.dispatchEvent(event);
}

function getAudioContext() {
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextClass) {
    return null;
  }

  try {
    if (!state.audioContext) {
      state.audioContext = new AudioContextClass();
    }

    const context = state.audioContext;
    if (context.state === "suspended") {
      context.resume().catch(() => {});
    }
    return context;
  } catch (error) {
    console.debug("Audio was blocked or unavailable.", error);
    return null;
  }
}

function playInvalidBuzz() {
  const now = performance.now();
  if (now - state.lastInvalidSoundAt < 160) {
    return;
  }
  state.lastInvalidSoundAt = now;
  boardEl.dataset.lastInvalidSoundAt = String(Math.round(now));

  try {
    const context = getAudioContext();
    if (!context) return;

    const oscillator = context.createOscillator();
    const gain = context.createGain();
    const start = context.currentTime;

    oscillator.type = "sawtooth";
    oscillator.frequency.setValueAtTime(150, start);
    oscillator.frequency.exponentialRampToValueAtTime(88, start + 0.13);
    gain.gain.setValueAtTime(0.0001, start);
    gain.gain.exponentialRampToValueAtTime(0.075, start + 0.015);
    gain.gain.exponentialRampToValueAtTime(0.0001, start + 0.15);

    oscillator.connect(gain);
    gain.connect(context.destination);
    oscillator.start(start);
    oscillator.stop(start + 0.16);
  } catch (error) {
    console.debug("Invalid-move sound was blocked or unavailable.", error);
  }
}

function handleInvalidMove(event) {
  boardEl.dataset.lastInvalidReason = event.detail.reason;
  playInvalidBuzz();

  const tileElement = boardEl.children[event.detail.tileIndex];
  if (!tileElement || tileElement.classList.contains("blank")) {
    return;
  }

  const existingTimer = invalidFeedbackTimers.get(tileElement);
  if (existingTimer) {
    window.clearTimeout(existingTimer);
  }

  tileElement.classList.remove("invalid-attempt");
  void tileElement.offsetWidth;
  tileElement.classList.add("invalid-attempt");

  const timer = window.setTimeout(() => {
    tileElement.classList.remove("invalid-attempt");
    invalidFeedbackTimers.delete(tileElement);
  }, 340);
  invalidFeedbackTimers.set(tileElement, timer);
}

function launchConfetti() {
  if (state.confettiCleanupId !== null) {
    clearTimeout(state.confettiCleanupId);
    state.confettiCleanupId = null;
  }
  confettiLayerEl.innerHTML = "";
  confettiLayerEl.dataset.lastConfettiAt = String(Math.round(performance.now()));

  const fragment = document.createDocumentFragment();
  const pieceCount = 92;
  for (let index = 0; index < pieceCount; index += 1) {
    const piece = document.createElement("span");
    piece.className = "confetti-piece";
    piece.style.setProperty("--x", `${Math.random() * 100}vw`);
    piece.style.setProperty("--w", `${6 + Math.random() * 7}px`);
    piece.style.setProperty("--h", `${10 + Math.random() * 12}px`);
    piece.style.setProperty("--drift", `${-90 + Math.random() * 180}px`);
    piece.style.setProperty("--spin", `${180 + Math.random() * 720}deg`);
    piece.style.setProperty("--delay", `${Math.random() * 0.35}s`);
    piece.style.setProperty("--duration", `${2.2 + Math.random() * 1.15}s`);
    piece.style.setProperty("--color", CONFETTI_COLORS[index % CONFETTI_COLORS.length]);
    fragment.appendChild(piece);
  }

  confettiLayerEl.appendChild(fragment);
  state.confettiCleanupId = window.setTimeout(() => {
    confettiLayerEl.innerHTML = "";
    state.confettiCleanupId = null;
  }, 4200);
}

function playCelebrationSound() {
  const now = performance.now();
  if (now - state.lastCelebrationSoundAt < CELEBRATION_SOUND_COOLDOWN_MS) {
    return;
  }
  state.lastCelebrationSoundAt = now;
  boardEl.dataset.lastCelebrationSoundAt = String(Math.round(now));

  try {
    const context = getAudioContext();
    if (!context) return;

    const start = context.currentTime;
    const master = context.createGain();
    master.gain.setValueAtTime(0.0001, start);
    master.gain.exponentialRampToValueAtTime(0.12, start + 0.025);
    master.gain.exponentialRampToValueAtTime(0.0001, start + 0.62);
    master.connect(context.destination);

    [523.25, 659.25, 783.99].forEach((frequency, index) => {
      const oscillator = context.createOscillator();
      const gain = context.createGain();
      const noteStart = start + index * 0.08;
      oscillator.type = "triangle";
      oscillator.frequency.setValueAtTime(frequency, noteStart);
      gain.gain.setValueAtTime(0.0001, noteStart);
      gain.gain.exponentialRampToValueAtTime(0.24, noteStart + 0.025);
      gain.gain.exponentialRampToValueAtTime(0.0001, noteStart + 0.32);
      oscillator.connect(gain);
      gain.connect(master);
      oscillator.start(noteStart);
      oscillator.stop(noteStart + 0.34);
    });

    const cheer = context.createOscillator();
    const cheerGain = context.createGain();
    cheer.type = "sine";
    cheer.frequency.setValueAtTime(880, start + 0.24);
    cheer.frequency.exponentialRampToValueAtTime(1174.66, start + 0.48);
    cheerGain.gain.setValueAtTime(0.0001, start + 0.22);
    cheerGain.gain.exponentialRampToValueAtTime(0.08, start + 0.28);
    cheerGain.gain.exponentialRampToValueAtTime(0.0001, start + 0.64);
    cheer.connect(cheerGain);
    cheerGain.connect(master);
    cheer.start(start + 0.22);
    cheer.stop(start + 0.66);
  } catch (error) {
    console.debug("Celebration sound was blocked or unavailable.", error);
  }
}

function commitTileMove(tileIndex) {
  if (state.completed || state.loading) return;
  const move = blankMoveForTile(tileIndex);
  if (!move) {
    dispatchInvalidMove(tileIndex, "Tile is not orthogonally adjacent to the blank.");
    return;
  }

  const blankIndex = state.tiles.indexOf(0);
  const nextTiles = [...state.tiles];
  nextTiles[blankIndex] = nextTiles[tileIndex];
  nextTiles[tileIndex] = 0;
  state.tiles = nextTiles;
  state.moves += 1;
  updateMetrics();
  renderBoard();

  if (isGoal()) {
    completePuzzle();
  }
}

function beginTileDrag(event, tileIndex, tileElement) {
  if (state.completed || state.loading || (typeof event.button === "number" && event.button > 0)) return;
  event.preventDefault();

  const adjacency = blankAdjacencyForTile(tileIndex);
  const target = adjacency ? dragTargetOffset(tileIndex, tileElement) : { x: 0, y: 0 };
  const point = interactionPoint(event);
  const id = interactionId(event);
  state.drag = {
    pointerId: id,
    tileIndex,
    tileElement,
    startX: point.x,
    startY: point.y,
    targetX: target.x,
    targetY: target.y,
    adjacency,
    moved: false,
    committed: false,
  };
  tileElement.classList.add("dragging");
  if (typeof id === "number" && tileElement.setPointerCapture) {
    try {
      tileElement.setPointerCapture(id);
    } catch (error) {
      console.debug("Pointer capture was unavailable for this drag.", error);
    }
  }
}

function updateTileDrag(event) {
  const drag = state.drag;
  if (!drag || drag.pointerId !== interactionId(event)) return;
  event.preventDefault();

  const point = interactionPoint(event);
  const rawX = point.x - drag.startX;
  const rawY = point.y - drag.startY;
  const distance = Math.hypot(rawX, rawY);
  drag.moved = drag.moved || distance > 6;

  let visualX = clamp(rawX * 0.12, -18, 18);
  let visualY = clamp(rawY * 0.12, -18, 18);

  if (drag.adjacency) {
    if (drag.targetX !== 0) {
      visualX = clamp(rawX, Math.min(0, drag.targetX), Math.max(0, drag.targetX));
      visualY = clamp(rawY * 0.08, -10, 10);
    } else {
      visualX = clamp(rawX * 0.08, -10, 10);
      visualY = clamp(rawY, Math.min(0, drag.targetY), Math.max(0, drag.targetY));
    }
  }

  drag.tileElement.style.transform = `translate(${visualX}px, ${visualY}px)`;
}

function endTileDrag(event) {
  const drag = state.drag;
  if (!drag || drag.pointerId !== interactionId(event)) return;
  event.preventDefault();

  const point = interactionPoint(event);
  const rawX = point.x - drag.startX;
  const rawY = point.y - drag.startY;
  const targetDistance = Math.max(Math.abs(drag.targetX), Math.abs(drag.targetY));
  let shouldMove = false;
  let invalidReason = "Tile is not orthogonally adjacent to the blank.";

  if (drag.adjacency) {
    if (!drag.moved) {
      shouldMove = true;
    } else if (drag.targetX !== 0) {
      const projected = rawX * Math.sign(drag.targetX);
      shouldMove = projected >= targetDistance * 0.35 && Math.abs(rawY) <= targetDistance * 0.7;
      invalidReason = "Dragged tile was not released toward the blank.";
    } else {
      const projected = rawY * Math.sign(drag.targetY);
      shouldMove = projected >= targetDistance * 0.35 && Math.abs(rawX) <= targetDistance * 0.7;
      invalidReason = "Dragged tile was not released toward the blank.";
    }
  }

  drag.tileElement.classList.remove("dragging");
  drag.tileElement.style.transform = "";
  if (typeof drag.pointerId === "number" && drag.tileElement.releasePointerCapture) {
    try {
      drag.tileElement.releasePointerCapture(drag.pointerId);
    } catch (error) {
      console.debug("Pointer release was unavailable for this drag.", error);
    }
  }
  state.drag = null;

  if (shouldMove) {
    drag.committed = true;
    commitTileMove(drag.tileIndex);
  } else {
    dispatchInvalidMove(drag.tileIndex, invalidReason);
  }
}

function cancelTileDrag(event) {
  const drag = state.drag;
  if (!drag || drag.pointerId !== interactionId(event)) return;
  event.preventDefault();
  drag.tileElement.classList.remove("dragging");
  drag.tileElement.style.transform = "";
  state.drag = null;
  dispatchInvalidMove(drag.tileIndex, "Drag was canceled before a legal move completed.");
}

function renderBoard() {
  boardEl.style.setProperty("--size", state.size);
  boardEl.innerHTML = "";

  state.tiles.forEach((tile, index) => {
    const cell = document.createElement(tile === 0 ? "div" : "button");
    cell.className = tile === 0 ? "tile blank" : "tile";
    cell.setAttribute("role", "gridcell");
    cell.setAttribute("aria-label", tile === 0 ? "Blank space with axe decal" : `Tile ${tile}`);

    if (tile === 0) {
      const axe = document.createElement("span");
      axe.className = "axe-decal";
      axe.setAttribute("aria-hidden", "true");
      axe.innerHTML = "&#129683;";
      cell.appendChild(axe);
    } else {
      cell.type = "button";
      cell.textContent = String(tile);
      if (window.PointerEvent) {
        cell.addEventListener("pointerdown", (event) => beginTileDrag(event, index, cell));
        cell.addEventListener("pointermove", updateTileDrag);
        cell.addEventListener("pointerup", endTileDrag);
        cell.addEventListener("pointercancel", cancelTileDrag);
      } else {
        cell.addEventListener("mousedown", (event) => beginTileDrag(event, index, cell));
        cell.addEventListener("touchstart", (event) => beginTileDrag(event, index, cell), { passive: false });
      }
      cell.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          commitTileMove(index);
        }
      });
    }

    boardEl.appendChild(cell);
  });
}

async function loadNewPuzzle(difficulty = state.difficulty) {
  const requestId = state.loadRequestId + 1;
  state.loadRequestId = requestId;

  if (state.puzzleAbortController) {
    state.puzzleAbortController.abort();
  }

  const controller = window.AbortController ? new AbortController() : null;
  state.puzzleAbortController = controller;
  setGameLoading(true);

  try {
    const response = await fetch(`/api/new-puzzle?difficulty=${encodeURIComponent(difficulty)}`, {
      signal: controller?.signal,
    });
    if (!response.ok) {
      throw new Error("Unable to load puzzle");
    }
    const payload = await response.json();
    if (requestId !== state.loadRequestId) {
      return false;
    }
    resetGameSession(payload);
    return true;
  } catch (error) {
    if (error.name === "AbortError") {
      return false;
    }
    if (requestId === state.loadRequestId) {
      console.error(error);
      factEl.textContent = "The puzzle service is not available.";
    }
    return false;
  } finally {
    if (requestId === state.loadRequestId) {
      state.puzzleAbortController = null;
      setGameLoading(false);
    }
  }
}

function setDifficultyButton(activeKey) {
  difficultyButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.difficulty === activeKey);
  });
}

function loadUsername() {
  const saved = window.localStorage.getItem("puzzleUsername") || "";
  usernameInput.value = saved;
  usernameDisplay.textContent = saved ? `Playing as ${saved}` : "No username set";
}

function saveUsername() {
  const username = usernameInput.value.trim();
  if (username) {
    window.localStorage.setItem("puzzleUsername", username);
    usernameDisplay.textContent = `Playing as ${username}`;
  } else {
    window.localStorage.removeItem("puzzleUsername");
    usernameDisplay.textContent = "No username set";
  }
}

function completionSaveStatusElement() {
  return document.querySelector("#completion-save-status");
}

function setCompletionSaveStatus(message) {
  const statusElement = completionSaveStatusElement();
  if (statusElement) {
    statusElement.textContent = message;
  }
}

async function saveCompletionRecord() {
  const requestId = state.completionSaveId + 1;
  state.completionSaveId = requestId;
  const username = usernameInput.value.trim();
  if (!username) {
    boardEl.dataset.completionSaved = "false";
    setCompletionSaveStatus("Set a username before completing a puzzle to save results.");
    return;
  }

  setCompletionSaveStatus("Saving completion...");
  try {
    const response = await fetch("/api/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        board_size: state.size,
        duration_seconds: state.elapsedSeconds,
        move_count: state.moves,
      }),
    });
    const payload = await response.json();
    if (requestId !== state.completionSaveId) {
      return;
    }
    if (!response.ok || !payload.saved) {
      throw new Error(payload.detail || "Unable to save completion.");
    }
    boardEl.dataset.completionSaved = "true";
    boardEl.dataset.completionRecordId = String(payload.record.id);
    setCompletionSaveStatus(`Saved for ${payload.record.username}.`);
  } catch (error) {
    if (requestId !== state.completionSaveId) {
      return;
    }
    boardEl.dataset.completionSaved = "false";
    console.debug("Completion save failed.", error);
    setCompletionSaveStatus("Completion finished, but the record could not be saved.");
  }
}

function stopFacts() {
  if (state.factTimerId !== null) {
    clearInterval(state.factTimerId);
    state.factTimerId = null;
  }
  if (state.factCountdownId !== null) {
    clearInterval(state.factCountdownId);
    state.factCountdownId = null;
  }
}

function renderCurrentFact() {
  if (!state.facts.length) {
    factEl.textContent = "Puzzle facts are not available.";
    factCountdownBarEl.style.transform = "scaleX(0)";
    return;
  }

  factEl.textContent = state.facts[state.factIndex];
  state.factStartedAt = Date.now();
  factCountdownBarEl.style.transform = "scaleX(1)";
}

function updateFactCountdown() {
  if (state.factStartedAt === null || !state.facts.length) {
    factCountdownBarEl.style.transform = "scaleX(0)";
    return;
  }

  const elapsed = Date.now() - state.factStartedAt;
  const remaining = Math.max(0, FACT_ROTATION_MS - elapsed);
  factCountdownBarEl.style.transform = `scaleX(${remaining / FACT_ROTATION_MS})`;
}

function rotateFact() {
  state.factIndex = (state.factIndex + 1) % state.facts.length;
  renderCurrentFact();
}

function startFacts() {
  stopFacts();
  state.factIndex = 0;
  renderCurrentFact();
  if (state.facts.length <= 1) {
    return;
  }

  state.factTimerId = window.setInterval(rotateFact, FACT_ROTATION_MS);
  state.factCountdownId = window.setInterval(updateFactCountdown, FACT_COUNTDOWN_MS);
}

function solverAlgorithmLabel(algorithm) {
  const labels = {
    BFS: "BFS \u2014 MINIMUM-MOVE SEARCH",
    "A* Misplaced": "A* \u2014 MISPLACED TILES",
    "A* Manhattan": "A* \u2014 MANHATTAN DISTANCE",
  };
  return labels[algorithm] || algorithm;
}

function renderMiniBoard(container, tiles, size) {
  if (!container) {
    return;
  }

  container.style.setProperty("--mini-size", size);
  container.innerHTML = "";
  tiles.forEach((tile) => {
    const cell = document.createElement("span");
    cell.className = tile === 0 ? "mini-tile blank" : "mini-tile";
    cell.textContent = tile === 0 ? "_" : String(tile);
    container.appendChild(cell);
  });
}

function applyBlankMoveForSolver(tiles, size, move) {
  const blankIndex = tiles.indexOf(0);
  const row = Math.floor(blankIndex / size);
  const column = blankIndex % size;
  const offsets = {
    UP: [-1, 0],
    DOWN: [1, 0],
    LEFT: [0, -1],
    RIGHT: [0, 1],
  };
  const offset = offsets[move];

  if (!offset) {
    throw new Error(`Unknown solver move: ${move}`);
  }

  const nextRow = row + offset[0];
  const nextColumn = column + offset[1];
  if (nextRow < 0 || nextRow >= size || nextColumn < 0 || nextColumn >= size) {
    throw new Error(`Solver move leaves the board: ${move}`);
  }

  const swapIndex = nextRow * size + nextColumn;
  const nextTiles = [...tiles];
  nextTiles[blankIndex] = nextTiles[swapIndex];
  nextTiles[swapIndex] = 0;
  return nextTiles;
}

function buildSolverPlaybackStates(startTiles, moves, size) {
  const states = [[...startTiles]];
  let current = [...startTiles];
  moves.forEach((move) => {
    current = applyBlankMoveForSolver(current, size, move);
    states.push([...current]);
  });
  return states;
}

function renderSolverPlayback() {
  if (!state.solverPlaybackStates.length) {
    return;
  }

  const size = 3;
  const index = state.solverPlaybackIndex;
  const moves = state.solverPlaybackMoves;
  renderMiniBoard(solverPlaybackBoardEl, state.solverPlaybackStates[index], size);

  solverStepLabelEl.textContent = `Step ${index} of ${moves.length}`;
  solverPlaybackMoveEl.textContent =
    index === 0 ? "Start state" : `Move ${index}: ${moves[index - 1]} (blank movement)`;

  solverPrevStepButton.disabled = index === 0;
  solverNextStepButton.disabled = index >= state.solverPlaybackStates.length - 1;
  solverResetStepButton.disabled = index === 0;
}

function createSolverDetail(label, value) {
  const line = document.createElement("p");
  line.className = "solver-detail";

  const labelEl = document.createElement("span");
  labelEl.textContent = `${label}: `;
  line.appendChild(labelEl);
  line.append(document.createTextNode(String(value)));

  return line;
}

function renderMoveSequence(card, moves) {
  const label = document.createElement("p");
  label.className = "move-label";
  label.textContent = "Returned ordered move sequence";
  card.appendChild(label);

  if (!moves.length) {
    const empty = document.createElement("p");
    empty.className = "move-sequence-empty";
    empty.textContent = "(empty sequence)";
    card.appendChild(empty);
    return;
  }

  const list = document.createElement("ol");
  list.className = "move-sequence";
  moves.forEach((move) => {
    const item = document.createElement("li");
    item.textContent = move;
    list.appendChild(item);
  });
  card.appendChild(list);
}

function renderSolverResultCards(results) {
  solverResultsEl.innerHTML = "";

  results.forEach((result) => {
    const card = document.createElement("article");
    card.className = "solver-card";

    const title = document.createElement("h3");
    title.textContent = solverAlgorithmLabel(result.algorithm);
    card.appendChild(title);

    card.appendChild(createSolverDetail("Solved status", result.solved ? "Solved" : result.status));
    card.appendChild(createSolverDetail("Solution length", result.solution_length));
    card.appendChild(createSolverDetail("Expanded states", result.expanded_states));
    renderMoveSequence(card, result.moves || []);

    solverResultsEl.appendChild(card);
  });
}

function renderSolverComparison(results) {
  solverComparisonBodyEl.innerHTML = "";

  results.forEach((result) => {
    const row = document.createElement("tr");

    const algorithm = document.createElement("td");
    algorithm.textContent = solverAlgorithmLabel(result.algorithm);

    const length = document.createElement("td");
    length.textContent = String(result.solution_length);

    const expanded = document.createElement("td");
    expanded.textContent = String(result.expanded_states);

    row.append(algorithm, length, expanded);
    solverComparisonBodyEl.appendChild(row);
  });
}

async function loadSolverDemo() {
  try {
    const response = await fetch("/api/solver-demo?case=comparison");
    if (!response.ok) {
      throw new Error("Unable to load solver demonstration");
    }

    const payload = await response.json();
    const tiles = payload.state.tiles;
    const size = payload.state.size;
    renderMiniBoard(solverStartBoardEl, tiles, size);
    renderSolverComparison(payload.results);
    renderSolverResultCards(payload.results);

    const playbackResult = payload.results.find((result) => result.algorithm === "BFS") || payload.results[0];
    state.solverPlaybackMoves = [...(playbackResult.moves || [])];
    state.solverPlaybackStates = buildSolverPlaybackStates(tiles, state.solverPlaybackMoves, size);
    state.solverPlaybackIndex = 0;
    renderSolverPlayback();
  } catch (error) {
    console.error(error);
    solverResultsEl.textContent = "Solver demonstration is not available.";
  }
}

async function init() {
  const configResponse = await fetch("/api/config");
  const config = await configResponse.json();
  state.facts = config.facts || [];
  loadUsername();
  startFacts();
  await loadNewPuzzle(config.default_difficulty || "easy");
  await loadSolverDemo();
}

saveUsernameButton.addEventListener("click", saveUsername);
usernameInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    saveUsername();
  }
});

if (!window.PointerEvent) {
  window.addEventListener("mousemove", updateTileDrag);
  window.addEventListener("mouseup", endTileDrag);
  window.addEventListener("touchmove", updateTileDrag, { passive: false });
  window.addEventListener("touchend", endTileDrag);
  window.addEventListener("touchcancel", cancelTileDrag);
}

newPuzzleButton.addEventListener("click", () => loadNewPuzzle(state.difficulty));
boardEl.addEventListener("puzzle:invalid-move", handleInvalidMove);
window.addEventListener("pagehide", stopFacts);

solverPrevStepButton.addEventListener("click", () => {
  state.solverPlaybackIndex = Math.max(0, state.solverPlaybackIndex - 1);
  renderSolverPlayback();
});

solverNextStepButton.addEventListener("click", () => {
  state.solverPlaybackIndex = Math.min(
    state.solverPlaybackStates.length - 1,
    state.solverPlaybackIndex + 1
  );
  renderSolverPlayback();
});

solverResetStepButton.addEventListener("click", () => {
  state.solverPlaybackIndex = 0;
  renderSolverPlayback();
});

difficultyButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    const difficulty = button.dataset.difficulty;
    setDifficultyButton(difficulty);
    await loadNewPuzzle(difficulty);
  });
});

init().catch((error) => {
  console.error(error);
  factEl.textContent = "The puzzle service is not available.";
});
