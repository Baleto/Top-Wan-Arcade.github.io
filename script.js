// ================================
// Theme handling (light / dark)
// ================================
const THEME_KEY = "topwan.theme";

function applyTheme(theme) {
  const root = document.documentElement;
  const meta = document.getElementById("theme-color-meta");

  const finalTheme = theme === "light" ? "light" : "dark";
  root.setAttribute("data-theme", finalTheme);
  localStorage.setItem(THEME_KEY, finalTheme);

  const toggle = document.getElementById("themeToggle");
  if (toggle) {
    if (finalTheme === "light") {
      toggle.textContent = "☀️ Light";
    } else {
      toggle.textContent = "🌙 Dark";
    }
  }

  // update browser UI color
  if (meta) {
    meta.setAttribute(
      "content",
      finalTheme === "light" ? "#f3f4f6" : "#050816"
    );
  }
}

function detectInitialTheme() {
  const stored = localStorage.getItem(THEME_KEY);
  if (stored === "light" || stored === "dark") return stored;

  // system preference fallback
  const prefersLight = window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: light)").matches;
  return prefersLight ? "light" : "dark";
}

document.addEventListener("DOMContentLoaded", () => {
  // 1) Initialize theme
  applyTheme(detectInitialTheme());

  const toggle = document.getElementById("themeToggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "dark";
      applyTheme(current === "dark" ? "light" : "dark");
    });
  }

  // 2) Year in footer
  const yearSpan = document.getElementById("year");
  if (yearSpan) {
    yearSpan.textContent = new Date().getFullYear();
  }

  // 3) “Learn more” button scroll
  const learnMoreBtn = document.getElementById("learnMoreBtn");
  const infoSection = document.querySelector(".panel.panel-soft");
  if (learnMoreBtn && infoSection) {
    learnMoreBtn.addEventListener("click", () => {
      infoSection.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  // 4) Game card “Preview Concept” clicks
  const gameButtons = document.querySelectorAll(".game-launch-btn");
  gameButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const card = btn.closest(".game-card");
      const gameId = card?.dataset.game || "unknown";
      const title = card?.querySelector("h3")?.textContent?.trim() || "this game";

      // For now, just a friendly message.
      alert(
        `${title}\n\nThis is currently a concept preview.\n` +
        "Soon, it will connect to a Python-powered game engine and a dedicated play screen."
      );
    });
  });
});
