import { useNavigate } from "react-router-dom";

import {
  GitPullRequest,
  ArrowRight,
  Sparkles,
  Code2,
} from "lucide-react";

import { setActiveIssueId } from "../utils/sessions.js";

export default function IssueCard({ issue, repo: repoProp }) {
  const navigate = useNavigate();

  if (!issue) return null;

  const id = issue.issue_id ?? issue.id;

  const repo =
    issue.repo ??
    repoProp ??
    "unknown/repo";

  const title =
    issue.title ??
    `Issue #${id}`;

  const language =
    issue.language ??
    issue.required_technologies?.[0] ??
    null;

  const difficulty =
    issue.difficulty ??
    issue.complexity_level ??
    null;

  const matchScore =
    issue.matchScore ??
    issue.match_score ??
    0;

  const aiReason =
    issue.aiReason ??
    issue.reasoning ??
    null;

  const labels = Array.from(
    new Set([
      ...(issue.labels || []),
      ...(issue.is_beginner_friendly
        ? ["good first issue"]
        : []),
      ...(issue.matching_skills || []),
    ])
  );

  const radius = 18;

  const circumference =
    2 * Math.PI * radius;

  const strokeDashoffset =
    circumference -
    (matchScore / 100) *
      circumference;

  const isHighMatch =
    matchScore >= 90;

  const handleNavigate = () => {
    setActiveIssueId(id);
    navigate(
      `/contrib/issue/${id}`
    );
  };

  return (
    <div
      onClick={handleNavigate}
      className="group relative flex flex-col md:flex-row md:items-center justify-between gap-6 p-6 sm:p-7 rounded-2xl border border-white/10 bg-transparent shadow-[0_0_40px_-10px_rgba(139,92,246,0.2)] hover:border-white/20 hover:shadow-[0_0_50px_-10px_rgba(139,92,246,0.35)] transition-all duration-300 cursor-pointer overflow-hidden"
    >
      <div className="absolute top-0 left-0 w-full h-px bg-linear-to-r from-transparent via-indigo-500/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

      <div className="flex items-start gap-5 flex-1 min-w-0">
        <div className="w-11 h-11 rounded-full border border-white/10 bg-transparent grid place-items-center shrink-0 group-hover:border-indigo-500/30 transition-colors">
          {language === "Python" ||
          language === "python" ? (
            <Code2 className="w-5 h-5 text-white" />
          ) : (
            <GitPullRequest className="w-5 h-5 text-white" />
          )}
        </div>

        <div className="flex flex-col min-w-0">
          <div className="flex items-center gap-2 text-[11px] font-mono tracking-[0.14em] text-slate-500 uppercase">
            <span className="truncate">
              {repo}
            </span>

            <span className="text-slate-700">
              ·
            </span>

            <span className="text-slate-400">
              #{id}
            </span>
          </div>

          <h3 className="text-[19px] sm:text-xl font-semibold text-white mt-2 leading-snug tracking-tight group-hover:text-indigo-200 transition-colors">
            {title}
          </h3>

          <div className="flex flex-wrap items-center gap-2 mt-4">
            {difficulty && (
              <span className="px-2.5 py-1 text-[11px] font-mono uppercase tracking-wider rounded-md border border-white/10 bg-transparent text-white/90 leading-5">
                {difficulty}
              </span>
            )}

            {language && (
              <span className="px-2.5 py-1 text-[11px] font-mono uppercase tracking-wider rounded-md border border-white/10 bg-transparent text-white/90 leading-5">
                {language}
              </span>
            )}

            {labels.map(
              (label, index) => (
                <span
                  key={`${label}-${index}`}
                  className="px-2.5 py-1 text-[11px] font-mono uppercase tracking-wider rounded-md border border-white/10 bg-transparent text-white/90 leading-5"
                >
                  {label}
                </span>
              )
            )}
          </div>

          {aiReason && (
            <div className="flex items-start gap-2 mt-4 text-[12px] sm:text-[13px] text-slate-400 font-mono leading-6">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400/80 shrink-0 mt-1" />

              <span className="line-clamp-2">
                {aiReason}
              </span>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between md:justify-end gap-8 md:w-auto w-full border-t border-white/5 md:border-t-0 pt-5 md:pt-0">
        <div className="flex flex-col items-center justify-center shrink-0">
          <div className="relative w-14 h-14 flex items-center justify-center">
            <svg
              className="w-full h-full transform -rotate-90"
              viewBox="0 0 40 40"
            >
              <circle
                cx="20"
                cy="20"
                r={radius}
                fill="transparent"
                stroke="rgba(255,255,255,0.06)"
                strokeWidth="3"
              />

              <circle
                cx="20"
                cy="20"
                r={radius}
                fill="transparent"
                stroke={
                  isHighMatch
                    ? "#22c55e"
                    : "#64748b"
                }
                strokeWidth="3"
                strokeDasharray={
                  circumference
                }
                strokeDashoffset={
                  strokeDashoffset
                }
                strokeLinecap="round"
                className="transition-all duration-1000 ease-out"
              />
            </svg>

            <span
              className={`absolute text-[12px] font-bold font-mono ${
                isHighMatch
                  ? "text-green-500"
                  : "text-slate-400"
              }`}
            >
              {matchScore}%
            </span>
          </div>

          <span className="text-[10px] uppercase tracking-[0.18em] text-slate-500 mt-1.5 hidden md:block font-mono">
            Match
          </span>
        </div>

        <button
          type="button"
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-3 rounded-lg text-[11px] uppercase tracking-[0.16em] font-semibold font-mono transition-all duration-300 shrink-0 shadow-lg shadow-indigo-500/20"
          onClick={(event) => {
            event.stopPropagation();
            handleNavigate();
          }}
        >
          <span className="hidden sm:inline">
            Start Issue
          </span>

          <span className="sm:hidden">
            Start
          </span>

          <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  );
}