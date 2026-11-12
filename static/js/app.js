(() => {
  const state = {
    files: [],
    sampleJds: [],
    lastResults: null,
  };

  // DOM Elements
  const htmlEl = document.documentElement;
  const themeToggle = document.getElementById("themeToggle");
  const sunIcon = document.getElementById("sunIcon");
  const moonIcon = document.getElementById("moonIcon");
  const demoBtn = document.getElementById("demoBtn");
  const sampleJdSelect = document.getElementById("sampleJdSelect");
  const jdInput = document.getElementById("jdInput");
  const jdWordCount = document.getElementById("jdWordCount");
  const clearJdBtn = document.getElementById("clearJdBtn");
  const useSamplesCheckbox = document.getElementById("useSamplesCheckbox");
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");
  const fileListContainer = document.getElementById("fileListContainer");
  const fileCountLabel = document.getElementById("fileCountLabel");
  const fileList = document.getElementById("fileList");
  const clearFilesBtn = document.getElementById("clearFilesBtn");
  const screenBtn = document.getElementById("screenBtn");
  const screenBtnText = document.getElementById("screenBtnText");
  const screenSpinner = document.getElementById("screenSpinner");
  const errorBanner = document.getElementById("errorBanner");

  const resultsSection = document.getElementById("resultsSection");
  const kpiTotal = document.getElementById("kpiTotal");
  const kpiTopScore = document.getElementById("kpiTopScore");
  const kpiAvgScore = document.getElementById("kpiAvgScore");
  const kpiStrongCount = document.getElementById("kpiStrongCount");
  const jdSkillsCount = document.getElementById("jdSkillsCount");
  const jdYearsBadge = document.getElementById("jdYearsBadge");
  const jdSkillsList = document.getElementById("jdSkillsList");
  const searchInput = document.getElementById("searchInput");
  const tierFilter = document.getElementById("tierFilter");
  const exportCsvBtn = document.getElementById("exportCsvBtn");
  const candidatesList = document.getElementById("candidatesList");

  const detailModal = document.getElementById("detailModal");
  const closeModalBtn = document.getElementById("closeModalBtn");
  const modalCandidateName = document.getElementById("modalCandidateName");
  const modalCandidateMeta = document.getElementById("modalCandidateMeta");
  const modalBody = document.getElementById("modalBody");

  // Theme
  function applyTheme(theme) {
    htmlEl.setAttribute("data-theme", theme);
    localStorage.setItem("resume-ai-theme", theme);
    if (theme === "dark") {
      sunIcon.classList.remove("hidden");
      moonIcon.classList.add("hidden");
    } else {
      sunIcon.classList.add("hidden");
      moonIcon.classList.remove("hidden");
    }
  }

  applyTheme(localStorage.getItem("resume-ai-theme") || "light");
  themeToggle.addEventListener("click", () => {
    const next = htmlEl.getAttribute("data-theme") === "dark" ? "light" : "dark";
    applyTheme(next);
  });

  // Helpers
  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function showError(msg) {
    errorBanner.textContent = msg;
    errorBanner.classList.remove("hidden");
  }

  function clearError() {
    errorBanner.textContent = "";
    errorBanner.classList.add("hidden");
  }

  function updateWordCount() {
    const words = jdInput.value.trim() ? jdInput.value.trim().split(/\s+/).length : 0;
    jdWordCount.textContent = `${words} word${words === 1 ? "" : "s"}`;
  }

  jdInput.addEventListener("input", updateWordCount);
  clearJdBtn.addEventListener("click", () => {
    jdInput.value = "";
    sampleJdSelect.value = "";
    updateWordCount();
  });

  // Load Samples
  async function loadSamples() {
    try {
      const res = await fetch("/api/samples");
      if (!res.ok) return;
      const data = await res.json();
      state.sampleJds = data.job_descriptions || [];
      state.sampleJds.forEach((jd) => {
        const opt = document.createElement("option");
        opt.value = jd.id;
        opt.textContent = jd.title;
        sampleJdSelect.appendChild(opt);
      });
    } catch (err) {
      console.warn("Could not load sample JDs:", err);
    }
  }

  sampleJdSelect.addEventListener("change", () => {
    const selected = state.sampleJds.find((j) => j.id === sampleJdSelect.value);
    if (selected) {
      jdInput.value = selected.content;
      updateWordCount();
    }
  });

  // File Handling
  function addFiles(fileListObj) {
    const incoming = Array.from(fileListObj);
    const validExt = [".pdf", ".txt", ".md"];
    const rejected = [];

    incoming.forEach((file) => {
      const ext = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
      if (!validExt.includes(ext)) {
        rejected.push(file.name);
        return;
      }
      const exists = state.files.some((f) => f.name === file.name && f.size === file.size);
      if (!exists) {
        state.files.push(file);
      }
    });

    if (rejected.length > 0) {
      showError(`Skipped unsupported file(s): ${rejected.join(", ")}. Only PDF and TXT are supported.`);
    } else {
      clearError();
    }
    renderFileList();
  }

  function renderFileList() {
    if (state.files.length === 0) {
      fileListContainer.classList.add("hidden");
      fileList.innerHTML = "";
      return;
    }
    fileListContainer.classList.remove("hidden");
    fileCountLabel.textContent = `${state.files.length} file${state.files.length === 1 ? "" : "s"} selected`;
    fileList.innerHTML = state.files
      .map(
        (file, index) => `
        <li class="file-item">
          <div class="file-item-meta">
            <span class="badge badge-neutral">${escapeHtml(file.name.split(".").pop().toUpperCase())}</span>
            <span class="file-name">${escapeHtml(file.name)}</span>
            <span class="muted small">(${(file.size / 1024).toFixed(1)} KB)</span>
          </div>
          <button class="remove-file-btn" type="button" data-index="${index}" aria-label="Remove ${escapeHtml(file.name)}">&times;</button>
        </li>`
      )
      .join("");
  }

  fileList.addEventListener("click", (e) => {
    const btn = e.target.closest(".remove-file-btn");
    if (!btn) return;
    const idx = Number(btn.dataset.index);
    state.files.splice(idx, 1);
    renderFileList();
  });

  clearFilesBtn.addEventListener("click", () => {
    state.files = [];
    fileInput.value = "";
    renderFileList();
  });

  dropZone.addEventListener("click", () => fileInput.click());
  dropZone.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      fileInput.click();
    }
  });
  fileInput.addEventListener("change", (e) => addFiles(e.target.files));

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
  });
  dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    if (e.dataTransfer?.files?.length) {
      addFiles(e.dataTransfer.files);
    }
  });

  // Screening
  async function runScreening() {
    clearError();
    const jdText = jdInput.value.trim();
    if (!jdText) {
      showError("Please enter or load a Job Description before screening.");
      jdInput.focus();
      return;
    }

    const useSamples = useSamplesCheckbox.checked;
    if (state.files.length === 0 && !useSamples) {
      showError("Please upload at least one resume (PDF/TXT) or enable 'Include 5 Sample Resumes'.");
      return;
    }

    const formData = new FormData();
    formData.append("job_description", jdText);
    formData.append("use_samples", useSamples ? "true" : "false");
    state.files.forEach((file) => formData.append("resumes", file));

    screenBtn.disabled = true;
    screenBtnText.textContent = "Analyzing Resumes...";
    screenSpinner.classList.remove("hidden");

    try {
      const res = await fetch("/api/screen", { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) {
        showError(data.error || "Failed to screen resumes.");
        return;
      }

      if (data.file_errors?.length) {
        const warnText = data.file_errors.map((fe) => `${fe.filename}: ${fe.error}`).join(" | ");
        showError(`Some files were skipped: ${warnText}`);
      }

      state.lastResults = data;
      renderResults(data);
      resultsSection.classList.remove("hidden");
      resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (err) {
      showError("Network error while communicating with the screening server.");
    } finally {
      screenBtn.disabled = false;
      screenBtnText.textContent = "Screen & Rank Candidates";
      screenSpinner.classList.add("hidden");
    }
  }

  screenBtn.addEventListener("click", runScreening);

  demoBtn.addEventListener("click", () => {
    if (state.sampleJds.length > 0) {
      const defaultJd = state.sampleJds[0];
      sampleJdSelect.value = defaultJd.id;
      jdInput.value = defaultJd.content;
      updateWordCount();
    }
    useSamplesCheckbox.checked = true;
    runScreening();
  });

  // Render Results
  function getTierBadgeClass(tier) {
    if (tier === "Strong Match") return "badge-strong";
    if (tier === "Good Match") return "badge-good";
    if (tier === "Moderate Match") return "badge-moderate";
    return "badge-low";
  }

  function renderResults(data) {
    const candidates = data.candidates || [];
    const total = candidates.length;
    const topScore = total ? Math.max(...candidates.map((c) => c.overall_score)) : 0;
    const avgScore = total
      ? candidates.reduce((sum, c) => sum + c.overall_score, 0) / total
      : 0;
    const strongCount = candidates.filter((c) => c.overall_score >= 75).length;

    kpiTotal.textContent = total;
    kpiTopScore.textContent = `${topScore.toFixed(1)}%`;
    kpiAvgScore.textContent = `${avgScore.toFixed(1)}%`;
    kpiStrongCount.textContent = strongCount;

    const jdSkills = data.jd_skills || [];
    jdSkillsCount.textContent = jdSkills.length;
    jdSkillsList.innerHTML = jdSkills.length
      ? jdSkills.map((s) => `<span class="chip chip-primary">${escapeHtml(s)}</span>`).join("")
      : `<span class="muted small">No predefined skill keywords matched; ranking relies on TF-IDF semantic similarity.</span>`;

    if (data.jd_required_years) {
      jdYearsBadge.textContent = `Target Experience: ${data.jd_required_years}+ yrs`;
      jdYearsBadge.classList.remove("hidden");
    } else {
      jdYearsBadge.classList.add("hidden");
    }

    renderCandidateCards();
  }

  function renderCandidateCards() {
    if (!state.lastResults) return;
    const query = searchInput.value.trim().toLowerCase();
    const tier = tierFilter.value;

    const filtered = (state.lastResults.candidates || []).filter((c) => {
      const matchesTier = tier === "ALL" || c.match_tier === tier;
      if (!matchesTier) return false;
      if (!query) return true;
      const haystack = [
        c.candidate_name,
        c.filename,
        ...(c.all_skills || []),
      ]
        .join(" ")
        .toLowerCase();
      return haystack.includes(query);
    });

    if (filtered.length === 0) {
      candidatesList.innerHTML = `<div class="card"><p class="muted" style="margin:0;text-align:center;">No candidates match your current filter.</p></div>`;
      return;
    }

    candidatesList.innerHTML = filtered
      .map((c) => {
        const rankClass = c.rank <= 3 ? `rank-${c.rank}` : "";
        const expText =
          c.estimated_years_experience !== null && c.estimated_years_experience !== undefined
            ? `~${c.estimated_years_experience} yr(s) exp`
            : "Exp N/A";
        const contactParts = [c.email, c.phone, c.filename, expText].filter(Boolean);

        const matchedHtml = c.matched_skills.length
          ? c.matched_skills.slice(0, 10).map((s) => `<span class="chip chip-match">${escapeHtml(s)}</span>`).join("")
          : `<span class="muted small">None</span>`;

        const missingHtml = c.missing_skills.length
          ? c.missing_skills.slice(0, 8).map((s) => `<span class="chip chip-missing">${escapeHtml(s)}</span>`).join("")
          : `<span class="chip chip-match">All JD skills covered</span>`;

        return `
        <article class="candidate-card">
          <div class="candidate-top">
            <div class="candidate-identity">
              <div class="rank-badge ${rankClass}">#${c.rank}</div>
              <div>
                <div class="candidate-name-row">
                  <h3 class="candidate-name">${escapeHtml(c.candidate_name)}</h3>
                  <span class="badge ${getTierBadgeClass(c.match_tier)}">${escapeHtml(c.match_tier)}</span>
                </div>
                <p class="candidate-meta">${escapeHtml(contactParts.join(" • "))}</p>
              </div>
            </div>
            <div class="score-pill-box">
              <div class="overall-score">${c.overall_score.toFixed(1)}%</div>
              <div class="score-label">Match Score</div>
            </div>
          </div>

          <div class="metrics-bars">
            <div>
              <div class="metric-row-top"><span>Skill Match</span><span>${c.skill_match_score.toFixed(1)}%</span></div>
              <div class="progress-track"><div class="progress-fill success" style="width:${c.skill_match_score}%"></div></div>
            </div>
            <div>
              <div class="metric-row-top"><span>TF-IDF Similarity</span><span>${c.tfidf_score.toFixed(1)}%</span></div>
              <div class="progress-track"><div class="progress-fill" style="width:${c.tfidf_score}%"></div></div>
            </div>
            <div>
              <div class="metric-row-top"><span>Profile &amp; Experience</span><span>${c.experience_score.toFixed(1)}%</span></div>
              <div class="progress-track"><div class="progress-fill warning" style="width:${c.experience_score}%"></div></div>
            </div>
          </div>

          <div class="skills-comparison">
            <div>
              <p class="skills-col-title">Matched Skills (${c.matched_skills.length})</p>
              <div class="chip-group">${matchedHtml}</div>
            </div>
            <div>
              <p class="skills-col-title">Missing JD Skills (${c.missing_skills.length})</p>
              <div class="chip-group">${missingHtml}</div>
            </div>
          </div>

          <p class="candidate-summary">${escapeHtml(c.summary_report)}</p>

          <div class="candidate-footer">
            <button class="btn btn-outline btn-sm view-detail-btn" type="button" data-rank="${c.rank}">
              View Full Profile &amp; Sections
            </button>
          </div>
        </article>`;
      })
      .join("");
  }

  searchInput.addEventListener("input", renderCandidateCards);
  tierFilter.addEventListener("change", renderCandidateCards);

  // Modal
  candidatesList.addEventListener("click", (e) => {
    const btn = e.target.closest(".view-detail-btn");
    if (!btn || !state.lastResults) return;
    const rank = Number(btn.dataset.rank);
    const candidate = state.lastResults.candidates.find((c) => c.rank === rank);
    if (!candidate) return;

    modalCandidateName.textContent = `#${candidate.rank} ${candidate.candidate_name}`;
    modalCandidateMeta.textContent = [
      candidate.email,
      candidate.phone,
      `File: ${candidate.filename}`,
      `Parser: ${candidate.parser_used}`,
    ]
      .filter(Boolean)
      .join(" • ");

    const catEntries = Object.entries(candidate.skills_by_category || {});
    const categoriesHtml = catEntries.length
      ? catEntries
          .map(
            ([cat, skills]) => `
            <div style="margin-bottom:8px;">
              <strong class="small">${escapeHtml(cat)}:</strong>
              <div class="chip-group" style="margin-top:4px;">
                ${skills.map((s) => `<span class="chip chip-neutral">${escapeHtml(s)}</span>`).join("")}
              </div>
            </div>`
          )
          .join("")
      : `<p class="muted small">No skills extracted.</p>`;

    const eduHtml = candidate.education_lines?.length
      ? `<ul class="modal-list">${candidate.education_lines.map((l) => `<li>${escapeHtml(l)}</li>`).join("")}</ul>`
      : `<p class="muted small">No dedicated Education section detected.</p>`;

    const expHtml = candidate.experience_lines?.length
      ? `<ul class="modal-list">${candidate.experience_lines.map((l) => `<li>${escapeHtml(l)}</li>`).join("")}</ul>`
      : `<p class="muted small">No dedicated Experience section detected.</p>`;

    modalBody.innerHTML = `
      <div class="modal-section">
        <h4>Summary Report</h4>
        <p class="candidate-summary">${escapeHtml(candidate.summary_report)}</p>
      </div>
      <div class="modal-section">
        <h4>Extracted Skills by Category</h4>
        ${categoriesHtml}
      </div>
      <div class="modal-section">
        <h4>Experience Highlights</h4>
        ${expHtml}
      </div>
      <div class="modal-section">
        <h4>Education</h4>
        ${eduHtml}
      </div>
    `;

    detailModal.classList.remove("hidden");
  });

  function closeModal() {
    detailModal.classList.add("hidden");
  }

  closeModalBtn.addEventListener("click", closeModal);
  detailModal.addEventListener("click", (e) => {
    if (e.target === detailModal) closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !detailModal.classList.contains("hidden")) closeModal();
  });

  // CSV Export
  exportCsvBtn.addEventListener("click", async () => {
    if (!state.lastResults?.candidates?.length) return;
    try {
      const res = await fetch("/api/export-csv", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ candidates: state.lastResults.candidates }),
      });
      if (!res.ok) {
        showError("Failed to export CSV report.");
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "candidate_ranking_report.csv";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      showError("Error downloading CSV report.");
    }
  });

  loadSamples();
})();

