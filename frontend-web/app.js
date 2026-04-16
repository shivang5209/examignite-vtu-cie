const API_BASE = "http://127.0.0.1:8000";

const state = {
  token: null,
  user: null,
  subjects: [],
  selectedSubject: null,
  questions: [],
  selectedQuestion: null,
  sessionId: null,
};

const byId = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
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
  state.token = tokens.accessToken;
  state.user = await api("/auth/me");
}

async function loadSubjects() {
  state.subjects = await api("/subjects");
  const select = byId("subject-select");
  select.innerHTML = "";
  state.subjects.forEach((subject) => {
    const opt = document.createElement("option");
    opt.value = subject.id;
    opt.textContent = `${subject.courseCode} - ${subject.title}`;
    select.appendChild(opt);
  });
  state.selectedSubject = state.subjects[0]?.id || null;
}

async function loadQuestions() {
  if (!state.selectedSubject) return;
  state.questions = await api(`/subjects/${state.selectedSubject}/questions`);
  const list = byId("question-list");
  list.innerHTML = "";
  state.questions.forEach((question) => {
    const li = document.createElement("li");
    li.textContent = `[${question.marks}] ${question.text}`;
    li.onclick = () => {
      state.selectedQuestion = question;
      byId("selected-question").textContent = question.text;
    };
    list.appendChild(li);
  });
}

async function startSession() {
  if (!state.selectedSubject || !state.selectedQuestion) {
    byId("practice-msg").textContent = "Select a subject and question first.";
    return;
  }
  const payload = {
    subjectId: state.selectedSubject,
    questionId: state.selectedQuestion.id,
  };
  const session = await api("/practice-sessions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  state.sessionId = session.id;
  byId("practice-msg").textContent = `Session started: ${session.id}`;
}

async function submitAnswer() {
  if (!state.sessionId) {
    byId("practice-msg").textContent = "Start a session first.";
    return;
  }
  const answerText = byId("answer-text").value.trim();
  if (answerText.length < 10) {
    byId("practice-msg").textContent = "Answer is too short.";
    return;
  }
  const feedback = await api(`/practice-sessions/${state.sessionId}/submit`, {
    method: "POST",
    body: JSON.stringify({ answerText }),
  });
  byId("score-line").textContent = `Score: ${feedback.scoreRaw} raw / ${feedback.scoreNormalized} normalized`;
  byId("summary-line").textContent = feedback.summary;
  byId("concepts").innerHTML = `<strong>Covered:</strong> ${feedback.conceptCoverage.join(", ")}<br><strong>Missed:</strong> ${feedback.missedConcepts.join(", ")}`;
  byId("evidence").innerHTML = feedback.evidence
    .map((item) => `<p><strong>${item.sourceTitle}</strong><br>${item.snippet}</p>`)
    .join("");
  byId("practice-msg").textContent = "Answer submitted.";
}

function wireEvents() {
  byId("login-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    byId("login-msg").textContent = "";
    try {
      await login(byId("email").value, byId("password").value);
      await loadSubjects();
      byId("welcome-title").textContent = `Welcome, ${state.user.name}`;
      byId("user-role").textContent = `Role: ${state.user.role}`;
      byId("login-panel").classList.add("hidden");
      byId("dashboard").classList.remove("hidden");
    } catch (error) {
      byId("login-msg").textContent = error.message;
    }
  });

  byId("subject-select").addEventListener("change", (event) => {
    state.selectedSubject = event.target.value;
  });
  byId("load-questions-btn").addEventListener("click", loadQuestions);
  byId("start-session-btn").addEventListener("click", startSession);
  byId("submit-answer-btn").addEventListener("click", submitAnswer);
  byId("logout-btn").addEventListener("click", () => location.reload());
}

wireEvents();
