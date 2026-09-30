import { useNavigate } from "react-router-dom";
import { GitPullRequest, ArrowRight, Sparkles, Code2 } from "lucide-react";

export default function IssueCard({ issue }) {
  const navigate = useNavigate();

  const data = issue || {
    id: 42,
    repo: "demo/todo-api",
    title: "Fix whitespace handling when creating a todo",
    labels: ["good first issue", "pytest"],
    language: "Python",
    difficulty: "Beginner",
    matchScore: 94,
    aiReason: "You know Python and pytest. This issue involves basic string manipulation.",
  };

  const radius = 18;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (data.matchScore / 100) * circumference;
  const isHighMatch = data.matchScore >= 90;

  return (
    <div
      onClick={() => navigate(`/issue/${data.id}`)}
      className="group relative flex flex-col md:flex-row md:items-center justify-between gap-6 p-6 rounded-xl border border-white/5 bg-[#0d1018]/60 backdrop-blur-sm hover:bg-[#121622]/90 hover:border-white/15 transition-all duration-300 cursor-pointer overflow-hidden"
    >
      <div className="absolute top-0 left-0 w-full `h-px` `bg-linear-to-r` from-transparent via-indigo-500/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

      <div className="flex items-start gap-5 flex-1 min-w-0">
        <div className="w-10 h-10 rounded-full border border-white/10 bg-white/5 grid place-items-center shrink-0 group-hover:border-indigo-500/30 group-hover:bg-indigo-500/10 transition-colors">
          {data.language === "Python" ? (
            <Code2 className="w-5 h-5 text-white" />
          ) : (
            <GitPullRequest className="w-5 h-5 text-white" />
          )}
        </div>

        <div className="flex flex-col min-w-0">
          <div className="flex items-center gap-2 text-[10px] font-mono tracking-[0.15em] text-slate-500 uppercase">
            <span>{data.repo}</span>
            <span className="text-slate-700">·</span>
            <span className="text-slate-400">#{data.id}</span>
          </div>

          <h3 className="text-lg font-semibold text-white mt-1.5 truncate group-hover:text-indigo-200 transition-colors">
            {data.title}
          </h3>

          {/* All tags unified to white text as requested */}
          <div className="flex flex-wrap items-center gap-2 mt-3">
            {data.difficulty && (
              <span className="px-2 py-0.5 text-[10px] uppercase tracking-wider rounded border border-white/10 bg-white/10 text-white">
                {data.difficulty}
              </span>
            )}

            {data.language && (
              <span className="px-2 py-0.5 text-[10px] uppercase tracking-wider rounded border border-white/10 bg-white/10 text-white">
                {data.language}
              </span>
            )}

            {data.labels.map((label, index) => (
              <span key={index} className="px-2 py-0.5 text-[10px] uppercase tracking-wider rounded border border-white/10 bg-white/10 text-white">
                {label}
              </span>
            ))}
          </div>

          {data.aiReason && (
            <div className="flex items-center gap-1.5 mt-3 text-[11px] text-slate-500">
              <Sparkles className="w-3 h-3 text-indigo-400/80 shrink-0" />
              <span className="truncate">{data.aiReason}</span>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between md:justify-end gap-8 md:w-auto w-full border-t border-white/5 md:border-t-0 pt-4 md:pt-0">
        
        <div className="flex flex-col items-center justify-center shrink-0">
          <div className="relative w-12 h-12 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 40 40">
              <circle cx="20" cy="20" r={radius} fill="transparent" stroke="rgba(255,255,255,0.06)" strokeWidth="3" />
              <circle
                cx="20" cy="20" r={radius} fill="transparent"
                stroke={isHighMatch ? "#22c55e" : "#64748b"} 
                strokeWidth="3" strokeDasharray={circumference} strokeDashoffset={strokeDashoffset} strokeLinecap="round"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <span className={`absolute text-[10px] font-bold ${isHighMatch ? "text-green-500" : "text-slate-400"}`}>
              {data.matchScore}%
            </span>
          </div>
          <span className="text-[9px] uppercase tracking-[0.18em] text-slate-500 mt-1 hidden md:block">
            Match
          </span>
        </div>

        <button
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-lg text-[10px] uppercase tracking-[0.18em] font-semibold transition-all duration-300 shrink-0 shadow-lg shadow-indigo-500/20"
          onClick={(e) => {
            e.stopPropagation(); 
            navigate(`/issue/${data.id}`);
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