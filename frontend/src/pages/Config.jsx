import { useState } from "react";

import {
  Eye,
  EyeOff,
  Code,
  Sparkles,
  CheckCircle2,
} from "lucide-react";

export default function Config() {
  const [githubToken, setGithubToken] = useState("");
  const [llmKey, setLlmKey] = useState("");

  const [showGithub, setShowGithub] = useState(false);
  const [showLlm, setShowLlm] = useState(false);

  const [savedGithub, setSavedGithub] = useState(false);
  const [savedLlm, setSavedLlm] = useState(false);

  const handleSaveGithub = () => {
    if (!githubToken.trim()) return;

    setSavedGithub(true);

    setTimeout(() => {
      setSavedGithub(false);
    }, 2000);
  };

  const handleSaveLlm = () => {
    if (!llmKey.trim()) return;

    setSavedLlm(true);

    setTimeout(() => {
      setSavedLlm(false);
    }, 2000);
  };

  return (
    <div className="min-h-screen pt-32 pb-24">
      <div className="max-w-3xl mx-auto px-5">

        {/* ---------- Page Header ---------- */}
        <div className="mb-11 text-center">
          <span className="text-[11px] font-mono tracking-[0.2em] text-white/70 uppercase">
            Configuration
          </span>

          <h1 className="text-4xl md:text-5xl font-extrabold mt-3 tracking-tight text-white">
            Connect your developer tools.
          </h1>

          <p className="text-[15px] sm:text-base font-mono text-white/70 mt-4 max-w-2xl mx-auto leading-7">
            Configure your credentials to enable AI analysis and GitHub access.
          </p>
        </div>

        {/* ---------- GitHub Token Card ---------- */}
        <div className="rounded-2xl border border-white/10 bg-transparent p-6 sm:p-8 shadow-[0_0_40px_-10px_rgba(139,92,246,0.2)]">

          <div className="flex items-center gap-2.5 mb-6">
            <Code className="w-5 h-5 text-white" />

            <h2 className="text-[13px] font-mono font-semibold tracking-[0.15em] text-white uppercase">
              GitHub Configuration
            </h2>
          </div>

          <label className="block text-[12px] font-mono tracking-[0.15em] text-white/80 uppercase mb-3">
            Personal Access Token
          </label>

          {/* GitHub Token Input */}
          <div className="relative">
            <input
              type={showGithub ? "text" : "password"}
              value={githubToken}
              onChange={(e) =>
                setGithubToken(e.target.value)
              }
              placeholder="github_pat_••••••••••••••••"
              autoComplete="off"
              spellCheck={false}
              className="w-full px-4 py-3.5 pr-14 rounded-xl bg-[#0d1018] border border-white/20 text-white placeholder:text-white/35 focus:outline-none focus:border-violet-500/60 focus:shadow-[0_0_25px_-5px_rgba(139,92,246,0.5)] transition-all duration-200 font-mono text-[14px]"
            />

            {/* Show / Hide Button */}
            <button
              type="button"
              onClick={() =>
                setShowGithub((v) => !v)
              }
              aria-label={
                showGithub
                  ? "Hide GitHub token"
                  : "Show GitHub token"
              }
              className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 grid place-items-center rounded-lg bg-[#1a1f30] border border-white/20 text-white hover:bg-[#252b3c] hover:border-white/40 active:scale-95 transition-all duration-200 z-10"
            >
              {showGithub ? (
                <EyeOff
                  className="w-5 h-5"
                  strokeWidth={2.2}
                />
              ) : (
                <Eye
                  className="w-5 h-5"
                  strokeWidth={2.2}
                />
              )}
            </button>
          </div>

          <p className="text-[12px] font-mono text-white/60 mt-3 leading-6">
            Required for accessing GitHub repositories and issues.
          </p>

          <div className="mt-6 flex items-center justify-between gap-4">
            <button
              type="button"
              onClick={handleSaveGithub}
              className="inline-flex items-center justify-center gap-2 text-white px-6 py-3 rounded-xl font-mono font-semibold text-[13px] transition-all duration-300 border border-[#6d8cff] shadow-[0_0_18px_-4px_rgba(109,140,255,0.55)] hover:shadow-[0_0_26px_-4px_rgba(109,140,255,0.85)] hover:border-[#8aa3ff] active:scale-[0.98]"
              style={{
                background:
                  "linear-gradient(to right, rgba(109,140,255,0.12), rgba(109,140,255,0.05))",
              }}
            >
              Save Token
            </button>

            {savedGithub && (
              <span className="flex items-center gap-1.5 text-[12px] font-mono text-green-400">
                <CheckCircle2 className="w-4 h-4" />
                Token saved
              </span>
            )}
          </div>
        </div>

        {/* ---------- LLM API Key Card ---------- */}
        <div className="mt-6 rounded-2xl border border-white/10 bg-transparent p-6 sm:p-8 shadow-[0_0_40px_-10px_rgba(139,92,246,0.2)]">

          <div className="flex items-center gap-2.5 mb-6">
            <Sparkles className="w-5 h-5 text-white" />

            <h2 className="text-[13px] font-mono font-semibold tracking-[0.15em] text-white uppercase">
              AI Configuration
            </h2>
          </div>

          <label className="block text-[12px] font-mono tracking-[0.15em] text-white/80 uppercase mb-3">
            LLM API Key
          </label>

          {/* LLM API Key Input */}
          <div className="relative">
            <input
              type={showLlm ? "text" : "password"}
              value={llmKey}
              onChange={(e) =>
                setLlmKey(e.target.value)
              }
              placeholder="gsk_••••••••••••••••••••••••"
              autoComplete="off"
              spellCheck={false}
              className="w-full px-4 py-3.5 pr-14 rounded-xl bg-[#0d1018] border border-white/20 text-white placeholder:text-white/35 focus:outline-none focus:border-violet-500/60 focus:shadow-[0_0_25px_-5px_rgba(139,92,246,0.5)] transition-all duration-200 font-mono text-[14px]"
            />

            {/* Show / Hide Button */}
            <button
              type="button"
              onClick={() =>
                setShowLlm((v) => !v)
              }
              aria-label={
                showLlm
                  ? "Hide LLM API key"
                  : "Show LLM API key"
              }
              className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 grid place-items-center rounded-lg bg-[#1a1f30] border border-white/20 text-white hover:bg-[#252b3c] hover:border-white/40 active:scale-95 transition-all duration-200 z-10"
            >
              {showLlm ? (
                <EyeOff
                  className="w-5 h-5"
                  strokeWidth={2.2}
                />
              ) : (
                <Eye
                  className="w-5 h-5"
                  strokeWidth={2.2}
                />
              )}
            </button>
          </div>

          <p className="text-[12px] font-mono text-white/60 mt-3 leading-6">
            Used for AI-powered issue analysis, breakdowns, and hints.
          </p>

          <div className="mt-6 flex items-center justify-between gap-4">
            <button
              type="button"
              onClick={handleSaveLlm}
              className="inline-flex items-center justify-center gap-2 text-white px-6 py-3 rounded-xl font-mono font-semibold text-[13px] transition-all duration-300 border border-[#6d8cff] shadow-[0_0_18px_-4px_rgba(109,140,255,0.55)] hover:shadow-[0_0_26px_-4px_rgba(109,140,255,0.85)] hover:border-[#8aa3ff] active:scale-[0.98]"
              style={{
                background:
                  "linear-gradient(to right, rgba(109,140,255,0.12), rgba(109,140,255,0.05))",
              }}
            >
              Save Key
            </button>

            {savedLlm && (
              <span className="flex items-center gap-1.5 text-[12px] font-mono text-green-400">
                <CheckCircle2 className="w-4 h-4" />
                Key saved
              </span>
            )}
          </div>
        </div>

        {/* ---------- Security Notice ---------- */}
        <div className="mt-6 rounded-2xl border border-white/10 bg-transparent p-6 sm:p-8 shadow-[0_0_40px_-10px_rgba(34,211,238,0.15)]">

          <h2 className="text-[13px] font-mono font-semibold tracking-[0.15em] text-white uppercase mb-4">
            🔒 Credential Security
          </h2>

          <ul className="text-[13px] font-mono text-white/70 space-y-2 leading-6">
            <li>
              • Never share your API keys or tokens publicly.
            </li>

            <li>
              • Never commit credentials to a repository.
            </li>

            <li>
              • Use tokens with the minimum required permissions.
            </li>

            <li>
              • ContribPilot does not display saved credentials.
            </li>
          </ul>
        </div>

      </div>
    </div>
  );
}