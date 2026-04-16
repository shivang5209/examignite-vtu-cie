const API_BASE = "http://127.0.0.1:8000";
const STORAGE_KEYS = {
  token: "examignite.token",
  user: "examignite.user",
  drafts: "examignite.drafts",
};

const state = {
  auth: {
    token: localStorage.getItem(STORAGE_KEYS.token),
    user: parseJson(localStorage.getItem(STORAGE_KEYS.user)),
  },
  catalog: {
    currentSemester: "4",
    subjects: [],
    progressBySubject: {},
    questionsBySubject: {},
  },
  history: {
    attempts: [],
  },
  ui: {
    activeView: "home-view",
    selectedSubjectId: null,
    selectedQuestionId: null,
    filters: {
      marks: "",
      moduleNo: "",
      year: "",
      diagramExpected: false,
    },
  },
  practice: {
    currentSession: null,
    currentFeedback: null,
    drafts: parseJson(localStorage.getItem(STORAGE_KEYS.drafts)) || {},
  },
};

const $ = (id) => document.getElementById(id);

const els = {
  loginView: $("login-view"),
  appView: $("app-view"),
  loginForm: $("login-form"),
  loginMsg: $("login-msg"),
  globalMsg: $("global-msg"),
  headerGreeting: $("header-greeting"),
  userName: $("user-name"),
  userRole: $("user-role"),
  semesterFilter: $("semester-filter"),
  logoutBtn: $("logout-btn"),
  navPills: Array.from(document.querySelectorAll(".nav-pill")),
  heroTitle: $("hero-title"),
  heroSubtitle: $("hero-subtitle"),
  heroPracticeBtn: $("hero-practice-btn"),
  heroHistoryBtn: $("hero-history-btn"),
  insightAverage: $("insight-average"),
  insightAttempts: $("insight-attempts"),
  insightWeakTopic: $("insight-weak-topic"),
  subjectCards: $("subject-cards"),
  recentAttempts: $("recent-attempts"),
  subjectCode: $("subject-code"),
  subjectTitle: $("subject-title"),
  subjectMeta: $("subject-meta"),
  subjectProgressScore: $("subject-progress-score"),
  subjectProgressDetail: $("subject-progress-detail"),
  filterMarks: $("filter-marks"),
  filterModule: $("filter-module"),
  filterYear: $("filter-year"),
  filterDiagram: $("filter-diagram"),
  questionCards: $("question-cards"),
  selectedQuestionPreview: $("selected-question-preview"),
  openPracticeBtn: $("open-practice-btn"),
  practiceSubjectCode: $("practice-subject-code"),
  practiceQuestionTitle: $("practice-question-title"),
  practiceChips: $("practice-chips"),
  examinerPanel: $("examiner-panel"),
  answerText: $("answer-text"),
  draftStatus: $("draft-status"),
  sessionStatus: $("session-status"),
  practiceBackBtn: $("practice-back-btn"),
  startSessionBtn: $("start-session-btn"),
  submitAnswerBtn: $("submit-answer-btn"),
  feedbackScore: $("feedback-score"),
  feedbackSummary: $("feedback-summary"),
  feedbackDiagram: $("feedback-diagram"),
  coveredConcepts: $("covered-concepts"),
  missedConcepts: $("missed-concepts"),
  referenceAnswer: $("reference-answer"),
  feedbackEvidence: $("feedback-evidence"),
  retryAnswerBtn: $("retry-answer-btn"),
  feedbackSubjectBtn: $("feedback-subject-btn"),
  historyList: $("history-list"),
  historySubjectSelect: $("history-subject-select"),
  historyProgressPanel: $("history-progress-panel"),
};

function parseJson(value) {
  if (!value) return null;
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

function persistAuth() {
  if (state.auth.token) {
    localStorage.setItem(STORAGE_KEYS.token, state.auth.token);
  } else {
    localStorage.removeItem(STORAGE_KEYS.token);
  }

  if (state.auth.user) {
    localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(state.auth.user));
  } else {
    localStorage.removeItem(STORAGE_KEYS.user);
  }
}

function persistDrafts() {
  localStorage.setItem(STORAGE_KEYS.drafts, JSON.stringify(state.practice.drafts));
}

function setGlobalMessage(message = "", isError = false) {
  els.globalMsg.textContent = message;
  els.globalMsg.classList.toggle("error-text", Boolean(message && isError));
}

function showAuth() {
  els.loginView.classList.remove("hidden");
  els.appView.classList.add("hidden");
}

function showApp() {
  els.loginView.classList.add("hidden");
  els.appView.classList.remove("hidden");
}

function setActiveView(viewId) {
  state.ui.activeView = viewId;
  document.querySelectorAll(".view-section").forEach((section) => {
    section.classList.toggle("hidden", section.id !== viewId);
  });
  els.navPills.forEach((pill) => {
    pill.classList.toggle("is-active", pill.dataset.view === viewId);
  });
}

function clearSessionState() {
  state.practice.currentSession = null;
  state.practice.currentFeedback = null;
  els.sessionStatus.textContent = "Not started";
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const isFormData = options.body instanceof FormData;

  if (!isFormData && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  if (state.auth.token) {
    headers.Authorization = `Bearer ${state.auth.token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (response.status === 401) {
    logout(true);
    throw new Error("Your session expired. Please log in again.");
  }

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || "Request failed");
  }

  return response.status === 204 ? null : response.json();
}

async function login(email, password) {
  const tokens = await api("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  state.auth.token = tokens.accessToken;
  state.auth.user = await api("/auth/me");
  persistAuth();
}

function logout(fromExpiry = false) {
  state.auth.token = null;
  state.auth.user = null;
  state.catalog.subjects = [];
  state.catalog.progressBySubject = {};
  state.catalog.questionsBySubject = {};
  state.history.attempts = [];
  state.ui.selectedSubjectId = null;
  state.ui.selectedQuestionId = null;
  state.practice.currentFeedback = null;
  state.practice.currentSession = null;
  persistAuth();
  clearSessionState();
  showAuth();
  setGlobalMessage(fromExpiry ? "Session expired. Please log in again." : "");
}

function firstName(name) {
  return (name || "Student").split(" ")[0];
}

function formatScore(value) {
  if (value === null || value === undefined || value === "") return "--";
  const numeric = Number(value);
  return Number.isFinite(numeric) ? `${numeric.toFixed(1)} / 10` : String(value);
}

function formatDate(value) {
  if (!value) return "Recent";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function truncate(value, length) {
  if (!value) return "";
  return value.length > length ? `${value.slice(0, Math.max(length - 3, 1))}...` : value;
}

function getSelectedSubject() {
  return state.catalog.subjects.find((subject) => subject.id === state.ui.selectedSubjectId) || null;
}

function getSelectedQuestion() {
  const questions = state.catalog.questionsBySubject[state.ui.selectedSubjectId] || [];
  return questions.find((question) => question.id === state.ui.selectedQuestionId) || null;
}

function getDraftKey(questionId) {
  return `question:${questionId}`;
}

function uniqueSorted(values) {
  return Array.from(new Set(values.filter((value) => value !== undefined && value !== null && value !== ""))).sort((a, b) => {
    if (typeof a === "number" && typeof b === "number") return a - b;
    return String(a).localeCompare(String(b));
  });
}

function syncSelectOptions(select, values, defaultLabel, suffix = "") {
  const currentValue = select.value;
  select.innerHTML = [`<option value="">${defaultLabel}</option>`]
    .concat(values.map((value) => `<option value="${value}">${value}${suffix}</option>`))
    .join("");
  if (values.includes(currentValue)) {
    select.value = currentValue;
  }
}

function findQuestionById(questionId) {
  if (!questionId) return null;
  for (const subject of state.catalog.subjects) {
    const questions = state.catalog.questionsBySubject[subject.id] || [];
    const question = questions.find((item) => item.id === questionId);
    if (question) {
      return { ...question, subjectId: subject.id };
    }
  }
  return null;
}

function populateHistorySubjectSelect() {
  if (!state.catalog.subjects.length) {
    els.historySubjectSelect.innerHTML = `<option value="">No subjects</option>`;
    return;
  }

  els.historySubjectSelect.innerHTML = state.catalog.subjects
    .map((subject) => `<option value="${subject.id}">${subject.courseCode} | ${subject.title}</option>`)
    .join("");
  els.historySubjectSelect.value = state.ui.selectedSubjectId || state.catalog.subjects[0].id;
}

function buildWeakTopicCopy(progress) {
  if (!progress?.weakTopics?.length) return "No weak topics flagged yet.";
  return `Watch ${progress.weakTopics[0]}.`;
}

function getFilteredQuestions() {
  const questions = state.catalog.questionsBySubject[state.ui.selectedSubjectId] || [];
  return questions.filter((question) => {
    if (state.ui.filters.marks && String(question.marks) !== state.ui.filters.marks) return false;
    if (state.ui.filters.moduleNo && String(question.moduleNo) !== state.ui.filters.moduleNo) return false;
    if (state.ui.filters.year && String(question.year) !== state.ui.filters.year) return false;
    if (state.ui.filters.diagramExpected && !question.diagramExpected) return false;
    return true;
  });
}

function buildExaminerPanel(question) {
  const points = [
    "Answer with a clear opening definition or framing sentence for the core concept.",
    "Organize the answer in examinable chunks so each concept earns marks independently.",
    question.diagramExpected
      ? "Add a clean diagram or labelled figure where it strengthens explanation."
      : "Add one compact example or use-case to anchor the theory.",
  ];

  return `
    <div class="pill-list">
      ${points.map((point) => `<span class="chip">${point}</span>`).join("")}
    </div>
  `;
}

function renderSubjectEmpty() {
  els.subjectCode.textContent = "Subject";
  els.subjectTitle.textContent = "Choose a subject";
  els.subjectMeta.textContent = "No subject selected yet.";
  els.subjectProgressScore.textContent = "--";
  els.subjectProgressDetail.textContent = "";
  els.questionCards.innerHTML = `<div class="empty-state">Choose a subject from home to begin browsing questions.</div>`;
  els.selectedQuestionPreview.textContent = "Pick a question to begin focused writing.";
}

function renderQuestionCards() {
  const questions = getFilteredQuestions();
  if (!questions.length) {
    els.questionCards.innerHTML = `<div class="empty-state">No questions match this filter combination yet.</div>`;
    return;
  }

  els.questionCards.innerHTML = questions
    .map((question) => {
      const activeClass = question.id === state.ui.selectedQuestionId ? "is-active" : "";
      return `
        <button class="question-card ${activeClass}" data-question-id="${question.id}">
          <header>
            <div>
              <p class="eyebrow">Module ${question.moduleNo || "--"}</p>
              <h4>${question.text}</h4>
            </div>
            <span class="score-badge">${question.marks} marks</span>
          </header>
          <div class="metric-row">
            <span>${question.year || "Recent"}</span>
            <span>${question.diagramExpected ? "Diagram expected" : "Theory answer"}</span>
            <span>${question.cieType || "curated"}</span>
          </div>
        </button>
      `;
    })
    .join("");

  document.querySelectorAll("[data-question-id]").forEach((button) => {
    button.addEventListener("click", () => {
      state.ui.selectedQuestionId = button.dataset.questionId;
      renderQuestionCards();
      syncPracticeFromSelection();
    });
  });
}

function syncPracticeFromSelection() {
  const subject = getSelectedSubject();
  const question = getSelectedQuestion();
  clearSessionState();

  if (!subject || !question) {
    els.selectedQuestionPreview.textContent = "Pick a question to begin focused writing.";
    els.practiceSubjectCode.textContent = "Practice";
    els.practiceQuestionTitle.textContent = "Select a question from the subject browser.";
    els.practiceChips.innerHTML = "";
    els.examinerPanel.innerHTML = `<p class="muted-copy">Once a question is selected, this panel will summarize the answer frame and special expectations.</p>`;
    els.answerText.value = "";
    els.draftStatus.textContent = "Draft idle";
    return;
  }

  const draftKey = getDraftKey(question.id);
  els.selectedQuestionPreview.textContent = question.text;
  els.practiceSubjectCode.textContent = `${subject.courseCode} | Module ${question.moduleNo || "--"}`;
  els.practiceQuestionTitle.textContent = question.text;
  els.practiceChips.innerHTML = [
    `<span class="chip">${question.marks} marks</span>`,
    `<span class="chip">${question.year || "Recent paper"}</span>`,
    `<span class="chip ${question.diagramExpected ? "chip-accent" : ""}">${question.diagramExpected ? "Diagram expected" : "Concept-heavy theory"}</span>`,
  ].join("");
  els.examinerPanel.innerHTML = buildExaminerPanel(question);
  els.answerText.value = state.practice.drafts[draftKey] || "";
  els.draftStatus.textContent = state.practice.drafts[draftKey] ? "Draft restored" : "Draft idle";
}

function renderSubject() {
  const subject = getSelectedSubject();
  if (!subject) {
    renderSubjectEmpty();
    return;
  }

  const progress = state.catalog.progressBySubject[subject.id] || {};
  const questions = state.catalog.questionsBySubject[subject.id] || [];

  els.subjectCode.textContent = subject.courseCode;
  els.subjectTitle.textContent = subject.title;
  els.subjectMeta.textContent = `Semester ${subject.semester} | ${questions.length} curated questions | Internal target ${subject.marksDisplay || 10} marks`;
  els.subjectProgressScore.textContent = formatScore(progress.averageNormalizedScore);
  els.subjectProgressDetail.textContent = `${progress.attemptsCount || 0} attempts | ${progress.weakTopics?.length || 0} weak topic markers`;

  syncSelectOptions(els.filterMarks, uniqueSorted(questions.map((item) => item.marks)).map(String), "All marks", " marks");
  syncSelectOptions(els.filterModule, uniqueSorted(questions.map((item) => item.moduleNo)).map(String), "All modules", " module");
  syncSelectOptions(els.filterYear, uniqueSorted(questions.map((item) => item.year)).map(String), "All years");
  els.filterMarks.value = state.ui.filters.marks;
  els.filterModule.value = state.ui.filters.moduleNo;
  els.filterYear.value = state.ui.filters.year;
  els.filterDiagram.checked = state.ui.filters.diagramExpected;

  renderQuestionCards();
  populateHistorySubjectSelect();
  syncPracticeFromSelection();
}

function renderSubjectCards() {
  if (!state.catalog.subjects.length) {
    els.subjectCards.innerHTML = `<div class="empty-state">No subjects found for this semester yet.</div>`;
    return;
  }

  els.subjectCards.innerHTML = state.catalog.subjects
    .map((subject) => {
      const progress = state.catalog.progressBySubject[subject.id] || {};
      const activeClass = subject.id === state.ui.selectedSubjectId ? "is-active" : "";
      return `
        <button class="subject-card ${activeClass}" data-subject-id="${subject.id}">
          <header>
            <div>
              <p class="eyebrow">${subject.courseCode}</p>
              <h4>${subject.title}</h4>
            </div>
            <span class="score-badge">${formatScore(progress.averageNormalizedScore)}</span>
          </header>
          <div class="meta-row">
            <span>Sem ${subject.semester}</span>
            <span>${subject.totalQuestions || 0} questions</span>
            <span>${progress.attemptsCount || 0} attempts</span>
          </div>
          <p class="muted-copy">Internal target ${subject.marksDisplay || 10} marks. ${buildWeakTopicCopy(progress)}</p>
        </button>
      `;
    })
    .join("");

  document.querySelectorAll("[data-subject-id]").forEach((button) => {
    button.addEventListener("click", async () => {
      setGlobalMessage("Loading subject workspace...");
      await hydrateSubjectWorkspace(button.dataset.subjectId);
      setGlobalMessage("");
      setActiveView("subject-view");
    });
  });
}

function renderRecentAttempts() {
  if (!state.history.attempts.length) {
    els.recentAttempts.innerHTML = `<div class="empty-state">Your recent attempts will appear here after the first submission.</div>`;
    return;
  }

  els.recentAttempts.innerHTML = state.history.attempts
    .slice(0, 6)
    .map((attempt) => {
      const question = findQuestionById(attempt.questionId);
      const subject = question ? state.catalog.subjects.find((item) => item.id === question.subjectId) : null;
      return `
        <article class="attempt-card">
          <header>
            <div>
              <p class="eyebrow">${subject?.courseCode || "Attempt"}</p>
              <h4>${truncate(question?.text || "Review attempt feedback", 66)}</h4>
            </div>
            <span class="score-pill">${formatScore(attempt.scoreNormalized)}</span>
          </header>
          <div class="attempt-meta">
            <span>${formatDate(attempt.createdAt)}</span>
            <span>${attempt.missedConcepts?.length || 0} missed concepts</span>
          </div>
          <div class="hero-actions">
            <button class="btn btn-tertiary" data-open-attempt="${attempt.attemptId}">Review feedback</button>
          </div>
        </article>
      `;
    })
    .join("");

  wireAttemptButtons();
}

function buildHomeMetrics() {
  let scoreTotal = 0;
  let scoreCount = 0;
  let weakest = null;

  state.catalog.subjects.forEach((subject) => {
    const progress = state.catalog.progressBySubject[subject.id];
    if (!progress) return;
    if (typeof progress.averageNormalizedScore === "number") {
      scoreTotal += progress.averageNormalizedScore;
      scoreCount += 1;
    }
    if (!weakest && progress.weakTopics?.length) {
      weakest = progress.weakTopics[0];
    }
  });

  const nextQuestion = findNextQuestion();
  return {
    average: scoreCount ? `${(scoreTotal / scoreCount).toFixed(1)} / 10` : "Not enough attempts",
    weakest: weakest || "No weak topic yet",
    title: nextQuestion
      ? `Next best move: ${nextQuestion.subject.courseCode} practice`
      : "Start your first focused CIE answer",
    subtitle: nextQuestion
      ? `${nextQuestion.question.text} This keeps you moving on the topic where the payoff is highest.`
      : "Pick a subject, open a question, and begin building answer-writing confidence with grounded feedback.",
  };
}

function findNextQuestion() {
  const subject = getSelectedSubject() || state.catalog.subjects[0];
  if (!subject) return null;
  const question = (state.catalog.questionsBySubject[subject.id] || [])[0];
  return question ? { subject, question } : null;
}

function renderHome() {
  const metrics = buildHomeMetrics();
  els.heroTitle.textContent = metrics.title;
  els.heroSubtitle.textContent = metrics.subtitle;
  els.insightAverage.textContent = metrics.average;
  els.insightAttempts.textContent = `${state.history.attempts.length}`;
  els.insightWeakTopic.textContent = metrics.weakest;
  renderSubjectCards();
  renderRecentAttempts();
}

function renderHistory() {
  if (!state.history.attempts.length) {
    els.historyList.innerHTML = `<div class="empty-state">Your attempt history will appear here once you submit answers.</div>`;
  } else {
    els.historyList.innerHTML = state.history.attempts
      .map((attempt) => {
        const question = findQuestionById(attempt.questionId);
        const subject = question ? state.catalog.subjects.find((item) => item.id === question.subjectId) : null;
        return `
          <article class="timeline-card">
            <header>
              <div>
                <p class="eyebrow">${subject?.courseCode || "Attempt"}</p>
                <h4>${truncate(question?.text || "Review attempt feedback", 72)}</h4>
              </div>
              <span class="score-pill">${formatScore(attempt.scoreNormalized)}</span>
            </header>
            <div class="attempt-meta">
              <span>${formatDate(attempt.createdAt)}</span>
              <span>${attempt.conceptCoverage?.length || 0} covered concepts</span>
              <span>${attempt.missedConcepts?.length || 0} missed concepts</span>
            </div>
            <div class="hero-actions">
              <button class="btn btn-tertiary" data-open-attempt="${attempt.attemptId}">Open feedback</button>
            </div>
          </article>
        `;
      })
      .join("");
  }

  wireAttemptButtons();
  populateHistorySubjectSelect();

  const subject = getSelectedSubject();
  const progress = subject ? state.catalog.progressBySubject[subject.id] : null;
  if (!subject || !progress) {
    els.historyProgressPanel.innerHTML = `<div class="empty-state">Select a subject to see progress clusters.</div>`;
    return;
  }

  const weakTopicsMarkup = progress.weakTopics?.length
    ? progress.weakTopics.map((topic) => `<span class="chip chip-negative">${topic}</span>`).join("")
    : `<span class="chip">No weak topic cluster yet</span>`;

  els.historyProgressPanel.innerHTML = `
    <article class="progress-card">
      <header>
        <div>
          <p class="eyebrow">${subject.courseCode}</p>
          <h4>${subject.title}</h4>
        </div>
        <span class="score-badge">${formatScore(progress.averageNormalizedScore)}</span>
      </header>
      <div class="metric-row">
        <span>${progress.attemptsCount || 0} attempts</span>
        <span>${subject.totalQuestions || 0} tracked questions</span>
      </div>
      <p class="muted-copy">Use the weak-topic clusters below to decide what to rewrite next.</p>
      <div class="pill-list">${weakTopicsMarkup}</div>
    </article>
  `;
}

function renderFeedback(feedback) {
  els.feedbackScore.textContent = `${feedback.scoreNormalized} / 10 normalized | ${feedback.scoreRaw} raw`;
  els.feedbackSummary.textContent = feedback.summary || "Feedback ready.";
  els.feedbackDiagram.textContent = feedback.diagramSuggestion || "No diagram recommendation for this answer.";
  els.coveredConcepts.innerHTML = feedback.conceptCoverage?.length
    ? feedback.conceptCoverage.map((concept) => `<span class="chip">${concept}</span>`).join("")
    : `<span class="chip">No covered concepts identified yet</span>`;
  els.missedConcepts.innerHTML = feedback.missedConcepts?.length
    ? feedback.missedConcepts.map((concept) => `<span class="chip chip-negative">${concept}</span>`).join("")
    : `<span class="chip">Nothing significant missed</span>`;
  els.referenceAnswer.textContent = feedback.referenceAnswer || "Reference answer is not available for this attempt.";
  els.feedbackEvidence.innerHTML = feedback.evidence?.length
    ? feedback.evidence
        .map(
          (item) => `
            <article class="evidence-card">
              <p class="eyebrow">${item.sourceTitle || "Study Source"}</p>
              <p>${item.snippet || ""}</p>
            </article>
          `,
        )
        .join("")
    : `<div class="empty-state">No evidence snippets were returned for this attempt.</div>`;
}

function wireAttemptButtons() {
  document.querySelectorAll("[data-open-attempt]").forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        setGlobalMessage("Loading feedback...");
        const attempt = await api(`/attempts/${button.dataset.openAttempt}`);
        state.practice.currentFeedback = attempt;
        renderFeedback(attempt);
        setGlobalMessage("");
        setActiveView("feedback-view");
      } catch (error) {
        setGlobalMessage(error.message, true);
      }
    });
  });
}

async function hydrateSubjectWorkspace(subjectId) {
  if (!subjectId) {
    renderSubjectEmpty();
    return;
  }

  state.ui.selectedSubjectId = subjectId;
  const questions = state.catalog.questionsBySubject[subjectId] || [];
  if (!questions.some((question) => question.id === state.ui.selectedQuestionId)) {
    state.ui.selectedQuestionId = questions[0]?.id || null;
  }

  renderHome();
  renderSubject();
  renderHistory();
}

async function loadWorkspace() {
  const query = state.catalog.currentSemester
    ? `?semester=${encodeURIComponent(state.catalog.currentSemester)}`
    : "";
  const [subjects, attempts] = await Promise.all([
    api(`/subjects${query}`),
    api("/attempts/history"),
  ]);

  state.catalog.subjects = subjects;
  state.history.attempts = attempts;

  const [progressEntries, questionEntries] = await Promise.all([
    Promise.all(
      subjects.map(async (subject) => [subject.id, await api(`/subjects/${subject.id}/progress`)]),
    ),
    Promise.all(
      subjects.map(async (subject) => [subject.id, await api(`/subjects/${subject.id}/questions`)]),
    ),
  ]);

  state.catalog.progressBySubject = Object.fromEntries(progressEntries);
  state.catalog.questionsBySubject = Object.fromEntries(questionEntries);

  if (!state.ui.selectedSubjectId && subjects.length) {
    state.ui.selectedSubjectId = subjects[0].id;
  }

  await hydrateSubjectWorkspace(state.ui.selectedSubjectId);
}

async function bootstrapApp() {
  showApp();
  els.headerGreeting.textContent = `Welcome back, ${firstName(state.auth.user?.name)}`;
  els.userName.textContent = state.auth.user?.name || "Student";
  els.userRole.textContent = state.auth.user?.role || "student";
  setGlobalMessage("Loading your workspace...");
  await loadWorkspace();
  setGlobalMessage("");
  setActiveView("home-view");
}

function saveDraft() {
  const question = getSelectedQuestion();
  if (!question) return;
  state.practice.drafts[getDraftKey(question.id)] = els.answerText.value;
  persistDrafts();
  els.draftStatus.textContent = els.answerText.value.trim() ? "Draft saved locally" : "Draft cleared";
}

async function ensureSession() {
  const subject = getSelectedSubject();
  const question = getSelectedQuestion();
  if (!subject || !question) {
    throw new Error("Choose a subject and question before starting practice.");
  }

  if (state.practice.currentSession?.questionId === question.id) {
    return state.practice.currentSession;
  }

  const session = await api("/practice-sessions", {
    method: "POST",
    body: JSON.stringify({
      subjectId: subject.id,
      questionId: question.id,
    }),
  });
  state.practice.currentSession = session;
  els.sessionStatus.textContent = `Session live | ${truncate(session.id, 18)}`;
  return session;
}

async function submitCurrentAnswer() {
  const question = getSelectedQuestion();
  if (!question) {
    throw new Error("Choose a question before submitting.");
  }

  const answerText = els.answerText.value.trim();
  if (answerText.length < 30) {
    throw new Error("Write a more complete answer before submitting.");
  }

  const session = await ensureSession();
  const feedback = await api(`/practice-sessions/${session.id}/submit`, {
    method: "POST",
    body: JSON.stringify({ answerText }),
  });

  state.practice.currentFeedback = feedback;
  delete state.practice.drafts[getDraftKey(question.id)];
  persistDrafts();
  state.history.attempts = await api("/attempts/history");

  const subject = getSelectedSubject();
  if (subject) {
    state.catalog.progressBySubject[subject.id] = await api(`/subjects/${subject.id}/progress`);
  }

  renderHome();
  renderSubject();
  renderHistory();
  renderFeedback(feedback);
  setActiveView("feedback-view");
}

function bindEvents() {
  els.loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    els.loginMsg.textContent = "";
    try {
      await login($("email").value.trim(), $("password").value.trim());
      await bootstrapApp();
    } catch (error) {
      els.loginMsg.textContent = error.message;
    }
  });

  els.navPills.forEach((pill) => {
    pill.addEventListener("click", () => setActiveView(pill.dataset.view));
  });

  els.semesterFilter.addEventListener("change", async (event) => {
    state.catalog.currentSemester = event.target.value;
    state.ui.selectedSubjectId = null;
    state.ui.selectedQuestionId = null;
    clearSessionState();
    try {
      setGlobalMessage("Refreshing semester workspace...");
      await loadWorkspace();
      setGlobalMessage("");
    } catch (error) {
      setGlobalMessage(error.message, true);
    }
  });

  els.logoutBtn.addEventListener("click", () => logout(false));

  els.heroPracticeBtn.addEventListener("click", async () => {
    const nextQuestion = findNextQuestion();
    if (!nextQuestion) {
      setGlobalMessage("No question is ready yet for this semester.", true);
      return;
    }
    await hydrateSubjectWorkspace(nextQuestion.subject.id);
    state.ui.selectedQuestionId = nextQuestion.question.id;
    renderSubject();
    setActiveView("practice-view");
  });

  els.heroHistoryBtn.addEventListener("click", () => setActiveView("history-view"));
  els.openPracticeBtn.addEventListener("click", () => setActiveView("practice-view"));
  els.practiceBackBtn.addEventListener("click", () => setActiveView("subject-view"));

  els.filterMarks.addEventListener("change", (event) => {
    state.ui.filters.marks = event.target.value;
    renderQuestionCards();
    syncPracticeFromSelection();
  });
  els.filterModule.addEventListener("change", (event) => {
    state.ui.filters.moduleNo = event.target.value;
    renderQuestionCards();
    syncPracticeFromSelection();
  });
  els.filterYear.addEventListener("change", (event) => {
    state.ui.filters.year = event.target.value;
    renderQuestionCards();
    syncPracticeFromSelection();
  });
  els.filterDiagram.addEventListener("change", (event) => {
    state.ui.filters.diagramExpected = event.target.checked;
    renderQuestionCards();
    syncPracticeFromSelection();
  });

  let draftTimer = null;
  els.answerText.addEventListener("input", () => {
    window.clearTimeout(draftTimer);
    draftTimer = window.setTimeout(saveDraft, 180);
  });

  els.startSessionBtn.addEventListener("click", async () => {
    try {
      setGlobalMessage("Starting practice session...");
      await ensureSession();
      setGlobalMessage("Session ready. You can keep writing and submit when ready.");
    } catch (error) {
      setGlobalMessage(error.message, true);
    }
  });

  els.submitAnswerBtn.addEventListener("click", async () => {
    try {
      setGlobalMessage("Submitting your answer for evaluation...");
      await submitCurrentAnswer();
      setGlobalMessage("Feedback is ready.");
    } catch (error) {
      setGlobalMessage(error.message, true);
    }
  });

  els.retryAnswerBtn.addEventListener("click", () => setActiveView("practice-view"));
  els.feedbackSubjectBtn.addEventListener("click", () => setActiveView("subject-view"));

  els.historySubjectSelect.addEventListener("change", async (event) => {
    await hydrateSubjectWorkspace(event.target.value);
    setActiveView("history-view");
  });
}

async function start() {
  bindEvents();
  if (!state.auth.token) {
    showAuth();
    return;
  }

  try {
    if (!state.auth.user) {
      state.auth.user = await api("/auth/me");
      persistAuth();
    }
    await bootstrapApp();
  } catch (error) {
    logout(true);
    els.loginMsg.textContent = error.message;
  }
}

start();
