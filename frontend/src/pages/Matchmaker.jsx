import { useState } from "react";
import { Search } from "lucide-react";
import IssueCard from "../components/IssueCard.jsx";
import { findIssues } from "../services/api.js";
import { saveMatchCriteria } from "../utils/sessions.js";

const LEVELS = ["Beginner", "Intermediate", "Advanced"];

export default function Matchmaker() {
  const [skills, setSkills] = useState("");
  const [level, setLevel] = useState("");
  const [repo, setRepo] = useState("");
  const [issues, setIssues] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFindIssue = async () => {
    if (!skills.trim() || !level || !repo.trim()) return;

    const skillsArr = skills
      .split(",")
      .map((s) => s.trim().toLowerCase())
      .filter(Boolean);

    const experience = level.toLowerCase();

    try {
      setLoading(true);
      setError(null);

      saveMatchCriteria({ skills: skillsArr, experience, repo });

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

  // ---------- Results view ----------
  if (issues !== null) {
    return (
      <div className="min-h-screen pt-32 pb-24">
        <div className="max-w-3xl mx-auto px-5">
          <div className="mb-8 flex items-end justify-between">
            <div>
              <span className="text-[10px] font-mono tracking-[0.2em] text-white uppercase">
                Results
              </span>
              <h1 className="text-3xl md:text-4xl font-extrabold mt-2 text-white">
                {issues.length} issue{issues.length !== 1 ? "s" : ""} found
              </h1>
              <p className="text-white/60 mt-1 font-mono text-sm">{repo}</p>
            </div>
            <button
              onClick={() => setIssues(null)}
              className="text-[11px] font-mono text-white/60 hover:text-white"
            >
              ← New search
            </button>
          </div>

          <div className="space-y-4">
            {issues.map((issue) => (
              <IssueCard key={issue.issue_id} issue={issue} repo={repo} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ---------- Form view ----------
  return (
    <div className="min-h-screen pt-32 pb-24">
      <div className="max-w-3xl mx-auto px-5">
        <div className="mb-10 text-center">
          <span className="text-[10px] font-mono tracking-[0.2em] text-white uppercase">
            Issue Matchmaker
          </span>
          <h1 className="text-4xl md:text-5xl font-extrabold mt-3 tracking-tight text-white">
            Find an issue worth solving.
          </h1>
          <p className="text-white mt-3 max-w-2xl mx-auto">
            Tell ContribPilot what you know. We'll surface issues that fit your skills.
          </p>
        </div>

        <div className="rounded-2xl border border-white/10 bg-transparent p-6 sm:p-8 shadow-[0_0_40px_-10px_rgba(139,92,246,0.2)]">
          {/* repo input */}
          <div className="flex flex-col items-center mb-6">
            <label className="block text-xs font-mono tracking-[0.15em] text-white uppercase mb-3">
              Repository
            </label>
            <input
              value={repo}
              onChange={(e) => setRepo(e.target.value)}
              placeholder="e.g. ejwa/gitinspector"
              className="w-full max-w-xl px-4 py-3 rounded-xl bg-transparent border border-white/10 text-white placeholder:text-white/40 text-center focus:outline-none focus:border-violet-500/60 transition"
            />
          </div>

          {/* skills input */}
          <div className="flex flex-col items-center">
            <label className="block text-xs font-mono tracking-[0.15em] text-white uppercase mb-3">
              Your Skills
            </label>
            <input
              value={skills}
              onChange={(e) => setSkills(e.target.value)}
              placeholder="e.g. python, react"
              className="w-full max-w-xl px-4 py-3 rounded-xl bg-transparent border border-white/10 text-white placeholder:text-white/40 text-center focus:outline-none focus:border-violet-500/60 transition"
            />
          </div>

          {/* level chips */}
          <div className="mt-8 flex flex-col items-center">
            <label className="block text-xs font-mono tracking-[0.15em] text-white uppercase mb-3">
              Your Level
            </label>
            <div className="flex flex-wrap justify-center gap-2">
              {LEVELS.map((lvl) => (
                <button
                  key={lvl}
                  onClick={() => setLevel(lvl)}
                  className={`px-5 py-2.5 rounded-lg text-sm font-medium border transition text-white ${
                    level === lvl
                      ? "border-cyan-500/60 bg-cyan-500/10 shadow-[0_0_20px_-5px_rgba(34,211,238,0.5)]"
                      : "border-white/10 hover:border-white/20"
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>

          {/* find issue button */}
          <div className="mt-10 flex flex-col items-center">
            <button
              onClick={handleFindIssue}
              disabled={loading || !skills || !level || !repo}
              className="inline-flex items-center justify-center gap-2 text-white px-8 py-3.5 rounded-xl font-semibold transition-all duration-300 border border-[#6d8cff] shadow-[0_0_18px_-4px_rgba(109,140,255,0.55)] hover:shadow-[0_0_26px_-4px_rgba(109,140,255,0.85)] hover:border-[#8aa3ff] disabled:opacity-40 disabled:cursor-not-allowed"
              style={{
                background:
                  "linear-gradient(to right, rgba(109,140,255,0.12), rgba(109,140,255,0.05))",
              }}
            >
              <Search className="w-4 h-4" />
              <span>{loading ? "Searching…" : "Find Issue"}</span>
            </button>

            {error && (
              <p className="mt-4 text-[12px] font-mono text-red-300">
                {error}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}