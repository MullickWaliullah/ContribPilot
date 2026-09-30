// ---------- Env-based base URL ----------
const API_BASE = import.meta.env.VITE_API_URL || "";

// ---------- Endpoint registry ----------
// NOTE: /api/issues (plural) — matching FastAPI router prefix
const ENDPOINTS = {
  recommend: "/api/issues/recommend",
  breakdown: (id) => `/api/issues/${id}/breakdown`,
  hint: "/api/contributions/hint",
};

// ---------- Headers ----------
function getHeaders() {
  return {
    "Content-Type": "application/json",
    "X-Github-Token": localStorage.getItem("gh_token") || "",
    "X-Groq-Api-Key": localStorage.getItem("llm_key") || "",
  };
}

// ---------- Generic request ----------
async function request(path, body) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    let message = "";

    try {
      const j = await res.json();
      // Backend can return multiple error shapes:
      //   HTTPException       → { detail: "..." }
      //   Custom handlers     → { error: "...", message: "..." }
      //   ValidationError     → { error, message, details: [...] }
      //   Pydantic default    → { detail: [{...}] }
      message =
        (typeof j.detail === "string" && j.detail) ||
        j.message ||
        j.error ||
        (Array.isArray(j.detail) &&
          j.detail.map((d) => d.msg || d.message).filter(Boolean).join(", ")) ||
        "";
    } catch {
      /* non-JSON body */
    }

    throw new Error(message || `Request failed (${res.status})`);
  }

  return res.json();
}

// ---------- Public API ----------

// STEP 1: Find matching issues
// body: { skills: string[], experience: string, repo: string, limit: number }
export function findIssues({ skills, experience, repo, limit = 10 }) {
  return request(ENDPOINTS.recommend, {
    skills,
    experience,
    repo,
    limit,
  });
}

// STEP 2: Get issue breakdown
// URL param: issueId | body: { repo, skills, experience }
export function getIssueBreakdown({ issueId, repo, skills, experience }) {
  return request(ENDPOINTS.breakdown(issueId), {
    repo,
    skills,
    experience,
  });
}

// STEP 3: Get hint for a specific level
// body: { level, issue_context, current_progress }
export function getHint({ level, issue_context, current_progress }) {
  return request(ENDPOINTS.hint, {
    level,
    issue_context,
    current_progress,
  });
}