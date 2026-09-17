// DOM Elements
const usernameInput = document.getElementById("username-input");
const analyzeBtn = document.getElementById("analyze-btn");
const loader = document.getElementById("loader");
const errorBox = document.getElementById("error-box");
const results = document.getElementById("results");
const downloadPdfBtn = document.getElementById("download-pdf-btn");
const copyLinkBtn = document.getElementById("copy-link-btn");
const headerUsernameTag = document.getElementById("header-username-tag");
const presetChips = document.querySelectorAll(".preset-chip");
const tabBtns = document.querySelectorAll(".tab-btn");
const tabContents = document.querySelectorAll(".tab-content");

// Repo filter elements
const repoSearchInput = document.getElementById("repo-search");
const forkFilterSelect = document.getElementById("fork-filter");
const sortFilterSelect = document.getElementById("sort-filter");

let currentProfileData = null;
let allRawRepos = [];
let languageChart = null;
let yearChart = null;

// Event Listeners
analyzeBtn.addEventListener("click", analyzeProfile);
usernameInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") analyzeProfile();
});

// Preset Chips
presetChips.forEach(chip => {
  chip.addEventListener("click", () => {
    const user = chip.getAttribute("data-user");
    usernameInput.value = user;
    analyzeProfile();
  });
});

// Copy Share Link
if (copyLinkBtn) {
  copyLinkBtn.addEventListener("click", () => {
    const currentUrl = window.location.href;
    navigator.clipboard.writeText(currentUrl).then(() => {
      const origText = copyLinkBtn.textContent;
      copyLinkBtn.textContent = "✅ Link Copied!";
      setTimeout(() => copyLinkBtn.textContent = origText, 2000);
    });
  });
}

// Tab Navigation
tabBtns.forEach(btn => {
  btn.addEventListener("click", () => {
    tabBtns.forEach(b => b.classList.remove("active"));
    tabContents.forEach(c => c.classList.add("hidden"));

    btn.classList.add("active");
    const targetTab = btn.getAttribute("data-tab");
    document.getElementById(targetTab).classList.remove("hidden");
  });
});

// Repo Filters Live Events
if (repoSearchInput) repoSearchInput.addEventListener("input", filterAndRenderRepos);
if (forkFilterSelect) forkFilterSelect.addEventListener("change", filterAndRenderRepos);
if (sortFilterSelect) sortFilterSelect.addEventListener("change", filterAndRenderRepos);

async function analyzeProfile() {
  const username = usernameInput.value.trim();
  if (!username) {
    showError("Please enter a GitHub username first.");
    return;
  }

  hideError();
  results.classList.add("hidden");
  loader.classList.remove("hidden");
  analyzeBtn.disabled = true;

  try {
    const response = await fetch(`/api/analyze/${encodeURIComponent(username)}`);
    const data = await response.json();

    if (!response.ok) {
      showError(data.error || "Something went wrong. Please try again.");
      return;
    }

    currentProfileData = data;
    allRawRepos = data.repos || [];
    renderResults(data, username);
  } catch (err) {
    showError("Could not connect to the server. Please try again.");
  } finally {
    loader.classList.add("hidden");
    analyzeBtn.disabled = false;
  }
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function hideError() {
  errorBox.classList.add("hidden");
}

function renderResults(data, username) {
  results.classList.remove("hidden");

  // Reset to first tab
  tabBtns[0].click();

  // Header & PDF Link
  if (headerUsernameTag) headerUsernameTag.textContent = `@${username}`;
  if (downloadPdfBtn) {
    downloadPdfBtn.href = `/api/download-pdf/${encodeURIComponent(username)}`;
  }

  // Profile Card
  document.getElementById("avatar").src = data.profile.avatar_url;
  document.getElementById("profile-name").textContent = data.profile.name;
  document.getElementById("personality-badge").textContent = data.personality ? data.personality.split("—")[0].trim() : "Developer";
  document.getElementById("profile-bio").textContent = data.profile.bio || "No bio available";
  document.getElementById("profile-location").textContent = `📍 ${data.profile.location || "Location not specified"}`;
  document.getElementById("profile-stats").textContent =
    `👥 ${data.profile.followers.toLocaleString()} followers · ${data.profile.following.toLocaleString()} following · 📦 ${data.profile.public_repos} repos`;
  document.getElementById("profile-link").href = data.profile.html_url;

  const noReposMsg = document.getElementById("no-repos-msg");
  const metricsGrid = document.getElementById("metrics-grid");
  const repoCountBadge = document.getElementById("repo-count-badge");

  if (repoCountBadge) repoCountBadge.textContent = allRawRepos.length;

  if (data.no_repos) {
    noReposMsg.classList.remove("hidden");
    metricsGrid.innerHTML = "";
    return;
  }
  noReposMsg.classList.add("hidden");

  // Metrics Grid
  const scoreVal = data.metrics.score !== undefined ? `${data.metrics.score}/100` : "N/A";
  metricsGrid.innerHTML = `
    ${metricCard(scoreVal, "Profile Score 🎯", "score-val")}
    ${metricCard(data.metrics.total_repos, "Total Repos", "repos-val")}
    ${metricCard(data.metrics.total_stars.toLocaleString(), "Total Stars ⭐", "stars-val")}
    ${metricCard(data.metrics.total_forks.toLocaleString(), "Total Forks 🍴", "forks-val")}
    ${metricCard(data.profile.account_age + " yrs", "Account Age", "age-val")}
  `;

  // Personality & Top Repo
  document.getElementById("personality-box").textContent = data.personality;

  const topRepoBox = document.getElementById("top-repo-card");
  if (data.top_repo) {
    topRepoBox.innerHTML = `
      <a href="${data.top_repo.url}" target="_blank">${escapeHtml(data.top_repo.name)}</a>
      <span style="color:var(--gold); float:right;">⭐ ${data.top_repo.stars.toLocaleString()}</span>
      <div class="desc">${escapeHtml(data.top_repo.description)}</div>
    `;
  } else {
    topRepoBox.innerHTML = `<span class="muted">No public repositories.</span>`;
  }

  // Render Charts & Tables
  renderScoreBreakdown(data);
  renderInsightsList(data.insights || []);
  renderLanguageChart(data.languages || {});
  renderLanguageTable(data.languages || {});
  renderYearChart(data.repos_per_year || {});
  filterAndRenderRepos();
}

function metricCard(value, label, customId = "") {
  return `
    <div class="metric-card">
      <div class="value" id="${customId}">${value}</div>
      <div class="label">${label}</div>
    </div>
  `;
}

function escapeHtml(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// Score Progress Bars
function renderScoreBreakdown(data) {
  const details = data.score_details || [
    { category: "Profile Completeness", score: 15, max: 20 },
    { category: "Repository Activity", score: 20, max: 30 },
    { category: "Community & Stars", score: 15, max: 30 },
    { category: "Language Diversity", score: 10, max: 20 }
  ];

  const scoreSummaryBox = document.getElementById("score-summary-box");
  const scoreProgressList = document.getElementById("score-progress-list");

  const progressHtml = details.map(item => {
    const pct = Math.round((item.score / item.max) * 100);
    return `
      <div class="score-item">
        <div class="score-item-header">
          <span>${item.category}</span>
          <span style="color:var(--accent);">${item.score}/${item.max} (${pct}%)</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" style="width: ${pct}%;"></div>
        </div>
      </div>
    `;
  }).join("");

  if (scoreSummaryBox) scoreSummaryBox.innerHTML = progressHtml;
  if (scoreProgressList) scoreProgressList.innerHTML = progressHtml;
}

// Insights List
function renderInsightsList(insights) {
  const container = document.getElementById("insights-list");
  if (!container) return;

  if (insights.length === 0) {
    container.innerHTML = `<p class="muted">No specific insights calculated.</p>`;
    return;
  }

  container.innerHTML = insights.map(text => `
    <div class="insight-card">
      <span style="font-size:1.2rem;">💡</span>
      <div>${escapeHtml(text)}</div>
    </div>
  `).join("");
}

// Charts
function renderLanguageChart(languages) {
  const ctx = document.getElementById("language-chart");
  if (!ctx) return;
  const entries = Object.entries(languages);

  if (languageChart) languageChart.destroy();

  if (entries.length === 0) {
    ctx.getContext("2d").clearRect(0, 0, ctx.width, ctx.height);
    return;
  }

  const total = entries.reduce((sum, [, v]) => sum + v, 0);
  const main = [];
  let other = 0;
  entries.forEach(([lang, bytes]) => {
    if (bytes / total * 100 < 2) other += bytes;
    else main.push([lang, bytes]);
  });
  if (other > 0) main.push(["Other", other]);

  const palette = ["#60a5fa", "#a78bfa", "#f59e0b", "#34d399", "#f87171", "#fbbf24", "#818cf8", "#9ca3af"];

  languageChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: main.map(([lang]) => lang),
      datasets: [{
        data: main.map(([, bytes]) => bytes),
        backgroundColor: palette.slice(0, main.length),
        borderWidth: 0,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "right", labels: { color: "#e5e7eb", font: { family: "Inter" } } }
      }
    }
  });
}

function renderLanguageTable(languages) {
  const box = document.getElementById("language-table-box");
  if (!box) return;
  const entries = Object.entries(languages).sort((a, b) => b[1] - a[1]);

  if (entries.length === 0) {
    box.innerHTML = `<p class="muted" style="padding:1rem;">No language data available.</p>`;
    return;
  }

  let rows = entries.map(([lang, bytes]) =>
    `<tr><td>${escapeHtml(lang)}</td><td>${bytes.toLocaleString()} bytes</td></tr>`
  ).join("");

  box.innerHTML = `
    <table>
      <thead><tr><th>Language</th><th>Code Volume</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderYearChart(reposPerYear) {
  const ctx = document.getElementById("year-chart");
  if (!ctx) return;
  const years = Object.keys(reposPerYear);
  const counts = Object.values(reposPerYear);

  if (yearChart) yearChart.destroy();

  yearChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: years,
      datasets: [{
        label: "Repos Created",
        data: counts,
        backgroundColor: "#60a5fa",
        borderRadius: 6,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: "#e5e7eb" }, grid: { color: "#232d3f" } },
        y: { ticks: { color: "#e5e7eb" }, grid: { color: "#232d3f" }, beginAtZero: true }
      }
    }
  });
}

// Interactive Repo Search, Filter & Sort
function filterAndRenderRepos() {
  const box = document.getElementById("repo-table-box");
  if (!box) return;

  const searchTerm = repoSearchInput ? repoSearchInput.value.toLowerCase().trim() : "";
  const forkFilter = forkFilterSelect ? forkFilterSelect.value : "all";
  const sortBy = sortFilterSelect ? sortFilterSelect.value : "stars";

  let filtered = allRawRepos.filter(r => {
    const matchSearch = r.name.toLowerCase().includes(searchTerm) || (r.language && r.language.toLowerCase().includes(searchTerm));
    const matchFork = forkFilter === "all" ? true : forkFilter === "fork" ? r.fork : !r.fork;
    return matchSearch && matchFork;
  });

  // Sorting
  filtered.sort((a, b) => {
    if (sortBy === "stars") return b.stars - a.stars;
    if (sortBy === "forks") return b.forks - a.forks;
    if (sortBy === "name") return a.name.localeCompare(b.name);
    if (sortBy === "created") return b.created.localeCompare(a.created);
    return 0;
  });

  if (filtered.length === 0) {
    box.innerHTML = `<p class="muted" style="padding:1.5rem; text-align:center;">No repositories match the current filters.</p>`;
    return;
  }

  let rows = filtered.map(r => `
    <tr>
      <td><a href="${r.url}" target="_blank">${escapeHtml(r.name)}</a></td>
      <td><span class="badge-tag">${escapeHtml(r.language)}</span></td>
      <td>⭐ ${r.stars.toLocaleString()}</td>
      <td>🍴 ${r.forks.toLocaleString()}</td>
      <td>${r.fork ? "Fork" : "Source"}</td>
      <td>${r.created}</td>
    </tr>
  `).join("");

  box.innerHTML = `
    <table>
      <thead>
        <tr><th>Repository Name</th><th>Language</th><th>Stars</th><th>Forks</th><th>Type</th><th>Created Date</th></tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}
