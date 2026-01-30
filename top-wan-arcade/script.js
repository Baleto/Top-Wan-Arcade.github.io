// script.js

// ========== THEME TOGGLE ==========
(function () {
  const html = document.documentElement;
  const metaTheme = document.getElementById("theme-color-meta");
  const toggleBtn = document.getElementById("themeToggle");

  const DARK_COLOR = "#050816";
  const LIGHT_COLOR = "#f5f5ff";

  function applyTheme(theme) {
    html.setAttribute("data-theme", theme);
    if (metaTheme) {
      metaTheme.setAttribute("content", theme === "dark" ? DARK_COLOR : LIGHT_COLOR);
    }
    if (toggleBtn) {
      toggleBtn.textContent = theme === "dark" ? "🌙 Dark" : "☀️ Light";
    }
    try {
      localStorage.setItem("topwan.theme", theme);
    } catch (e) {
      // ignore
    }
  }

  function getInitialTheme() {
    try {
      const stored = localStorage.getItem("topwan.theme");
      if (stored === "dark" || stored === "light") return stored;
    } catch (e) {
      // ignore
    }
    return window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: light)").matches
      ? "light"
      : "dark";
  }

  const initial = getInitialTheme();
  applyTheme(initial);

  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      const next = html.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
    });
  }
})();

// ========== GSAP SPICE ==========
document.addEventListener("DOMContentLoaded", () => {
  if (typeof gsap === "undefined") return;

  // Hero text animation
  gsap.from(".hero-text", {
    opacity: 0,
    y: 20,
    duration: 0.8,
    ease: "power3.out"
  });

  // Hero card
  gsap.from(".hero-card", {
    opacity: 0,
    y: 28,
    duration: 0.9,
    ease: "power3.out",
    delay: 0.12
  });

  // Game cards - staggered
  gsap.from(".game-card", {
    opacity: 0,
    y: 22,
    scale: 0.97,
    duration: 0.7,
    ease: "power2.out",
    stagger: 0.08,
    delay: 0.15
  });
});

// ========== "Learn more" button ==========
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("learnMoreBtn");
  const infoSection = document.querySelector(".panel.panel-soft");

  if (!btn || !infoSection) return;

  btn.addEventListener("click", () => {
    infoSection.scrollIntoView({ behavior: "smooth", block: "start" });

    if (typeof gsap !== "undefined") {
      gsap.fromTo(
        infoSection,
        { boxShadow: "0 18px 40px rgba(0,0,0,0.8)" },
        {
          boxShadow: "0 0 0 1px rgba(250, 204, 21, 0.8), 0 22px 50px rgba(0,0,0,0.9)",
          duration: 0.35,
          yoyo: true,
          repeat: 1,
          ease: "power2.inOut"
        }
      );
    }
  });
});
