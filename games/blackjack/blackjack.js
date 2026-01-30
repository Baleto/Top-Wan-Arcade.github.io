const API = "http://127.0.0.1:5050/api/blackjack";

const dealerCards = document.getElementById("dealerCards");
const playerCards = document.getElementById("playerCards");
const dealerTotal = document.getElementById("dealerTotal");
const playerTotal = document.getElementById("playerTotal");
const statusMsg = document.getElementById("statusMsg");

const newBtn = document.getElementById("newBtn");
const hitBtn = document.getElementById("hitBtn");
const standBtn = document.getElementById("standBtn");
const statsBtn = document.getElementById("statsBtn");
const statsPanel = document.getElementById("statsPanel");
const statsGrid = document.getElementById("statsGrid");

const fullscreenBtn = document.getElementById("fullscreenBtn");
const stage = document.getElementById("stage");

function renderCards(el, cards) {
  el.innerHTML = "";
  cards.forEach(([r, s]) => {
    const d = document.createElement("div");
    d.className = "card";
    d.textContent = (r === "?" ? "🂠" : `${r}${s}`);
    el.appendChild(d);
  });
}

function setControls(phase) {
  const active = phase === "player_turn";
  hitBtn.disabled = !active;
  standBtn.disabled = !active;
}

function renderState(data) {
  renderCards(playerCards, data.player);
  renderCards(dealerCards, data.dealer);

  playerTotal.textContent = `Total: ${data.player_total}`;
  dealerTotal.textContent = data.dealer_total == null ? "" : `Total: ${data.dealer_total}`;

  statusMsg.textContent = data.message;
  setControls(data.phase);
}

async function apiPost(path) {
  const res = await fetch(`${API}/${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function apiGet(path) {
  const res = await fetch(`${API}/${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

newBtn.addEventListener("click", async () => {
  try {
    const data = await apiPost("new");
    renderState(data);
  } catch (e) {
    statusMsg.textContent = "Backend not running. Start it: backend/app.py";
  }
});

hitBtn.addEventListener("click", async () => {
  try {
    const data = await apiPost("hit");
    renderState(data);
  } catch (e) {
    statusMsg.textContent = "Error: couldn't HIT.";
  }
});

standBtn.addEventListener("click", async () => {
  try {
    const data = await apiPost("stand");
    renderState(data);
  } catch (e) {
    statusMsg.textContent = "Error: couldn't STAND.";
  }
});

statsBtn.addEventListener("click", async () => {
  const open = !statsPanel.hidden;
  statsPanel.hidden = open;
  if (!open) {
    try {
      const s = await apiGet("stats");
      statsGrid.innerHTML = `
        <div class="stat-box"><strong>You Wins</strong><div>${s.bj_user_wins}</div></div>
        <div class="stat-box"><strong>CPU Wins</strong><div>${s.bj_cpu_wins}</div></div>
        <div class="stat-box"><strong>Naturals</strong><div>${s.bj_blackjacks}</div></div>
        <div class="stat-box"><strong>Best Streak</strong><div>${s.bj_best_streak}</div></div>
      `;
    } catch {
      statsGrid.innerHTML = `<div class="stat-box">Start the backend to view stats.</div>`;
    }
  }
});

fullscreenBtn.addEventListener("click", async () => {
  try {
    if (!document.fullscreenElement) {
      await stage.requestFullscreen();
    } else {
      await document.exitFullscreen();
    }
  } catch {
    // no-op
  }
});
