import { useState } from "react";

import { Search } from "lucide-react";

import IssueCard from "../components/IssueCard.jsx";

import { findIssues } from "../services/api.js";

import { saveMatchCriteria } from "../utils/sessions.js";

const LEVELS = [
  "Beginner",
  "Intermediate",
  "Advanced",
];

export default function Matchmaker() {
  const [skills, setSkills] = useState("");
  const [level, setLevel] = useState("");
  const [repo, setRepo] = useState("");

  const [issues, setIssues] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFindIssue = async () => {
    if (
      !skills.trim() ||
      !level ||
      !repo.trim()
    ) {
      return;
    }

    const skillsArr = skills
      .split(",")
      .map((s) => s.trim().toLowerCase())
      .filter(Boolean);

    const experience = level.toLowerCase();

    try {
      setLoading(true);
      setError(null);

      saveMatchCriteria({
        skills: skillsArr,
        experience,
        repo,
      });

      const data = await findIssues({
        skills: skillsArr,
        experience,
        repo,
        limit: 10,
      });

      setIssues(data.issues || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  if (issues !== null) {
    return (
      <div className="min-h-screen pt-32 pb-24">
        <div className="max-w-3xl mx-auto px-5">

          <div className="mb-9 flex items-end justify-between gap-4">
            <div>
              <span className="text-[11px] font-mono tracking-[0.2em] text-white/70 uppercase">
                Results
              </span>

              <h1 className="text-3xl md:text-4xl font-extrabold mt-2 tracking-tight text-white">
                {issues.length} issue
                {issues.length !== 1 ? "s" : ""} found
              </h1>

              <p className="text-[14px] text-white/60 mt-2 font-mono break-all">
                {repo}
              </p>
            </div>

            <button
              onClick={() => setIssues(null)}
              className="shrink-0 text-[12px] font-mono text-white/60 hover:text-white transition-colors"
            >
              ← New search
            </button>
          </div>

          <div className="space-y-4">
            {issues.map((issue) => (
              <IssueCard
                key={issue.issue_id}
                issue={issue}
                repo={repo}
              />
            ))}
          </div>

        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-32 pb-24">
      <div className="max-w-3xl mx-auto px-5">

        <div className="mb-11 text-center">
          <span className="text-[11px] font-mono tracking-[0.2em] text-white/70 uppercase">
            Issue Matchmaker
          </span>

          <h1 className="text-4xl md:text-5xl font-extrabold mt-3 tracking-tight text-white">
            Find an issue worth solving.
          </h1>

          <p className="text-[15px] sm:text-base text-white/70 mt-4 max-w-2xl mx-auto leading-7 font-mono">
            Tell ContribPilot what you know. We'll surface issues that fit your skills.
          </p>
        </div>

        <div className="rounded-2xl border border-white/10 bg-transparent p-6 sm:p-8 shadow-[0_0_40px_-10px_rgba(139,92,246,0.2)]">

          <div className="flex flex-col items-center mb-7">
            <label className="block text-[12px] font-mono tracking-[0.15em] text-white/80 uppercase mb-3">
              Repository
            </label>

            <input
              value={repo}
              onChange={(e) =>
                setRepo(e.target.value)
              }
              placeholder="e.g. ejwa/gitinspector"
              className="w-full max-w-xl px-4 py-3.5 rounded-xl bg-transparent border border-white/10 text-white placeholder:text-white/35 text-[15px] font-mono text-center focus:outline-none focus:border-violet-500/60 focus:shadow-[0_0_20px_-8px_rgba(139,92,246,0.45)] transition"
            />
          </div>

          <div className="flex flex-col items-center">
            <label className="block text-[12px] font-mono tracking-[0.15em] text-white/80 uppercase mb-3">
              Your Skills
            </label>

            <input
              value={skills}
              onChange={(e) =>
                setSkills(e.target.value)
              }
              placeholder="e.g. python, react"
              className="w-full max-w-xl px-4 py-3.5 rounded-xl bg-transparent border border-white/10 text-white placeholder:text-white/35 text-[15px] font-mono text-center focus:outline-none focus:border-violet-500/60 focus:shadow-[0_0_20px_-8px_rgba(139,92,246,0.45)] transition"
            />
          </div>

          <div className="mt-9 flex flex-col items-center">
            <label className="block text-[12px] font-mono tracking-[0.15em] text-white/80 uppercase mb-3">
              Your Level
            </label>

            <div className="flex flex-wrap justify-center gap-2.5">
              {LEVELS.map((lvl) => (
                <button
                  key={lvl}
                  onClick={() =>
                    setLevel(lvl)
                  }
                  className={`px-5 py-2.5 rounded-lg text-[13px] font-mono font-medium border transition-all text-white ${
                    level === lvl
                      ? "border-cyan-500/60 bg-cyan-500/10 shadow-[0_0_20px_-5px_rgba(34,211,238,0.5)]"
                      : "border-white/10 hover:border-white/25 hover:bg-white/[0.03]"
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-11 flex flex-col items-center">
            <button
              onClick={handleFindIssue}
              disabled={
                loading ||
                !skills ||
                !level ||
                !repo
              }
              className="inline-flex items-center justify-center gap-2.5 text-white px-8 py-3.5 rounded-xl font-mono font-semibold text-[13px] transition-all duration-300 border border-[#6d8cff] shadow-[0_0_18px_-4px_rgba(109,140,255,0.55)] hover:shadow-[0_0_26px_-4px_rgba(109,140,255,0.85)] hover:border-[#8aa3ff] disabled:opacity-40 disabled:cursor-not-allowed"
              style={{
                background:
                  "linear-gradient(to right, rgba(109,140,255,0.12), rgba(109,140,255,0.05))",
              }}
            >
              <Search className="w-4 h-4" />

              <span>
                {loading
                  ? "Searching…"
                  : "Find Issue"}
              </span>
            </button>

            {error && (
              <p className="mt-4 text-[13px] font-mono text-red-300 leading-6 text-center">
                {error}
              </p>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}