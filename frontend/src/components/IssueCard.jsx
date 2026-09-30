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

  // ---------- Normalize backend → frontend ----------
  const id = issue.issue_id ?? issue.id;
  const repo = issue.repo ?? repoProp ?? "unknown/repo";
  const title = issue.title ?? `Issue #${id}`;
  const language = issue.language ?? issue.required_technologies?.[0] ?? null;
  const difficulty = issue.difficulty ?? issue.complexity_level ?? null;
  const matchScore = issue.matchScore ?? issue.match_score ?? 0;
  const aiReason = issue.aiReason ?? issue.reasoning ?? null;

  // Combine backend fields into a single labels list (dedup)
  const labels = Array.from(
    new Set([
      ...(issue.labels || []),
      ...(issue.is_beginner_friendly ? ["good first issue"] : []),
      ...(issue.matching_skills || []),
    ])
  );

  const radius = 18;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (matchScore / 100) * circumference;
  const isHighMatch = matchScore >= 90;

  const handleNavigate = () => {
    setActiveIssueId(id);
    navigate(`/contrib/issue/${id}`);
  };

  return (
    <div
      onClick={handleNavigate}
      className="group relative flex flex-col md:flex-row md:items-center justify-between gap-6 p-6 rounded-2xl border border-white/10 bg-transparent shadow-[0_0_40px_-10px_rgba(139,92,246,0.2)] hover:border-white/20 hover:shadow-[0_0_50px_-10px_rgba(139,92,246,0.35)] transition-all duration-300 cursor-pointer overflow-hidden"
    >
      <div className="absolute top-0 left-0 w-full h-px bg-linear-to-r from-transparent via-indigo-500/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

      <div className="flex items-start gap-5 flex-1 min-w-0">
        <div className="w-10 h-10 rounded-full border border-white/10 bg-transparent grid place-items-center shrink-0 group-hover:border-indigo-500/30 transition-colors">
          {language === "Python" || language === "python" ? (
            <Code2 className="w-5 h-5 text-white" />
          ) : (
            <GitPullRequest className="w-5 h-5 text-white" />
          )}
        </div>

        <div className="flex flex-col min-w-0">
          <div className="flex items-center gap-2 text-[10px] font-mono tracking-[0.15em] text-slate-500 uppercase">
            <span>{repo}</span>
            <span className="text-slate-700">·</span>
            <span className="text-slate-400">#{id}</span>
          </div>

          <h3 className="text-lg font-semibold text-white mt-1.5 truncate group-hover:text-indigo-200 transition-colors">
            {title}
          </h3>

          <div className="flex flex-wrap items-center gap-2 mt-3">
            {difficulty && (
              <span className="px-2 py-0.5 text-[10px] uppercase tracking-wider rounded border border-white/10 bg-transparent text-white">
                {difficulty}
              </span>
            )}
            {language && (
              <span className="px-2 py-0.5 text-[10px] uppercase tracking-wider rounded border border-white/10 bg-transparent text-white">
                {language}
              </span>
            )}
            {labels.map((label, index) => (
              <span
                key={`${label}-${index}`}
                className="px-2 py-0.5 text-[10px] uppercase tracking-wider rounded border border-white/10 bg-transparent text-white"
              >
                {label}
              </span>
            ))}
          </div>

          {aiReason && (
            <div className="flex items-center gap-1.5 mt-3 text-[11px] text-slate-500">
              <Sparkles className="w-3 h-3 text-indigo-400/80 shrink-0" />
              <span className="truncate">{aiReason}</span>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between md:justify-end gap-8 md:w-auto w-full border-t border-white/5 md:border-t-0 pt-4 md:pt-0">
        <div className="flex flex-col items-center justify-center shrink-0">
          <div className="relative w-12 h-12 flex items-center justify-center">
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
                stroke={isHighMatch ? "#22c55e" : "#64748b"}
                strokeWidth="3"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                className="transition-all duration-1000 ease-out"
              />
            </svg>

            <span
              className={`absolute text-[10px] font-bold ${
                isHighMatch ? "text-green-500" : "text-slate-400"
              }`}
            >
              {matchScore}%
            </span>
          </div>

          <span className="text-[9px] uppercase tracking-[0.18em] text-slate-500 mt-1 hidden md:block">
            Match
          </span>
        </div>

        <button
          type="button"
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-lg text-[10px] uppercase tracking-[0.18em] font-semibold transition-all duration-300 shrink-0 shadow-lg shadow-indigo-500/20"
          onClick={(event) => {
            event.stopPropagation();
            handleNavigate();
          }}
        >
          <span className="hidden sm:inline">Start Issue</span>
          <span className="sm:hidden">Start</span>
          <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  );
}