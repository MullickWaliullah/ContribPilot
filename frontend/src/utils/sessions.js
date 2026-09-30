const CRITERIA_KEY = "cp_match_criteria";
const ACTIVE_ISSUE_KEY = "active_issue_id";
const hintKey = (issueId) => `cp_hint_${issueId}`;

// ---------- Match criteria (skills/experience/repo) ----------
export function saveMatchCriteria({ skills, experience, repo }) {
  try {
    localStorage.setItem(
      CRITERIA_KEY,
      JSON.stringify({ skills, experience, repo })
    );
  } catch {
    /* ignore storage errors */
  }
}

export function getMatchCriteria() {
  try {
    const raw = localStorage.getItem(CRITERIA_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

// ---------- Active issue (last viewed) ----------
export function setActiveIssueId(id) {
  try {
    localStorage.setItem(ACTIVE_ISSUE_KEY, String(id));
  } catch {}
}

export function getActiveIssueId() {
  try {
    return localStorage.getItem(ACTIVE_ISSUE_KEY);
  } catch {
    return null;
  }
}

// ---------- Hint unlock progress ----------
export function getUnlockedHint(issueId) {
  try {
    return Number(localStorage.getItem(hintKey(issueId)) || 0);
  } catch {
    return 0;
  }
}

export function setUnlockedHint(issueId, level) {
  try {
    localStorage.setItem(hintKey(issueId), String(level));
  } catch {}
}