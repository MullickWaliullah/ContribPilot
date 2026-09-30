import { useState } from "react";
import {
  Lightbulb,
  Lock,
  Loader2,
  CheckCircle2,
  FileCode2,
  Hash,
  TestTube2,
  Target,
  Focus,
} from "lucide-react";
import { getHint } from "../services/api.js";
import { getUnlockedHint, setUnlockedHint } from "../utils/sessions.js";

// ---------- Safe JSON parse for nested hint_text ----------
function parseHintPayload(raw) {
  if (raw == null) return null;

  // If already an object, return as-is
  if (typeof raw === "object") return raw;

  if (typeof raw !== "string") return null;

  // Try JSON.parse, fall back to plain text
  try {
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object") return parsed;
    return { focus_summary: String(parsed) };
  } catch {
    return { focus_summary: raw };
  }
}

// ---------- Small inline chip list ----------
function MiniChipList({ label, items = [], icon: Icon }) {
  if (!items || !items.length) return null;
  return (
    <div className="mt-3">
      <div className="flex items-center gap-1.5 mb-2">
        {Icon && <Icon className="w-3 h-3 text-white/60" />}
        <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-white/60">
          {label}
        </span>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {items.map((item, i) => (
          <span
            key={i}
            className="px-2 py-1 text-[10px] font-mono rounded-md border border-white/15 text-white/85"
          >
            {typeof item === "string" ? item : JSON.stringify(item)}
          </span>
        ))}
      </div>
    </div>
  );
}

// ---------- Render a single hint's structured content ----------
function HintContent({ payload }) {
  if (!payload) return null;

  const {
    focus_summary,
    files_to_check = [],
    symbols_to_inspect = [],
    relevant_tests = [],
    areas_of_interest = [],
    guidance_level,
  } = payload;

  const hasAny =
    focus_summary ||
    files_to_check.length ||
    symbols_to_inspect.length ||
    relevant_tests.length ||
    areas_of_interest.length;

  if (!hasAny) {
    return (
      <p className="text-[12px] font-mono text-white/60 italic">
        No hint content provided.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {focus_summary && (
        <p className="text-sm text-white/85 font-mono leading-relaxed whitespace-pre-wrap">
          {focus_summary}
        </p>
      )}

      <MiniChipList
        label="Files to check"
        items={files_to_check}
        icon={FileCode2}
      />
      <MiniChipList
        label="Symbols to inspect"
        items={symbols_to_inspect}
        icon={Hash}
      />
      <MiniChipList
        label="Relevant tests"
        items={relevant_tests}
        icon={TestTube2}
      />
      <MiniChipList
        label="Areas of interest"
        items={areas_of_interest}
        icon={Target}
      />

      {guidance_level != null && (
        <div className="pt-2 text-[10px] font-mono uppercase tracking-[0.15em] text-white/40">
          Guidance level {guidance_level}
        </div>
      )}
    </div>
  );
}

// ---------- Main component ----------
export default function HintCard({
  issueId,
  issueContext = {},
  currentProgress = {},
}) {
  const [unlocked, setUnlocked] = useState(() => getUnlockedHint(issueId));
  const [hints, setHints] = useState({}); // { 1: payloadObj, 2: ..., 3: ... }
  const [loading, setLoading] = useState(null);
  const [error, setError] = useState(null);

  const handleUnlock = async (level) => {
    // Sequential guard
    if (level > 1 && unlocked < level - 1) {
      setError(`Pehle hint ${level - 1} unlock karo.`);
      return;
    }

    setError(null);
    setLoading(level);

    try {
      const data = await getHint({
        level,
        issue_context: issueContext,
        current_progress: currentProgress,
      });

      // Backend returns { level, hint_text }
      // hint_text is a STRINGIFIED JSON — parse it
      const raw = data.hint_text ?? data.hint ?? data.text ?? data.content;
      const parsed = parseHintPayload(raw) ?? {};

      setHints((prev) => ({ ...prev, [level]: parsed }));

      if (level > unlocked) {
        setUnlocked(level);
        setUnlockedHint(issueId, level);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(null);
    }
  };

  const levels = [1, 2, 3];

  return (
    <div className="rounded-2xl border border-white/10 bg-transparent p-6 sm:p-7 shadow-[0_0_40px_-10px_rgba(139,92,246,0.2)]">
      <div className="flex items-center gap-2 mb-5">
        <Lightbulb className="w-4 h-4 text-white" />
        <h2 className="text-xs font-mono tracking-[0.15em] text-white uppercase">
          Guided Hints
        </h2>
      </div>

      <div className="space-y-3">
        {levels.map((level) => {
          const isUnlocked = unlocked >= level;
          const isAvailable = unlocked + 1 >= level;
          const isLoading = loading === level;
          const payload = hints[level];

          return (
            <div
              key={level}
              className={`rounded-xl border p-4 transition ${
                isUnlocked
                  ? "border-green-500/30"
                  : isAvailable
                  ? "border-[#6d8cff]/40"
                  : "border-white/10 opacity-60"
              }`}
            >
              <div className="flex items-center justify-between gap-3 mb-3">
                <div className="flex items-center gap-2">
                  <Focus className="w-3.5 h-3.5 text-white/70" />
                  <span className="text-[10px] font-mono tracking-[0.15em] text-white/70 uppercase">
                    Hint {level}
                  </span>
                </div>

                {isUnlocked && (
                  <span className="flex items-center gap-1 text-[10px] font-mono text-green-400">
                    <CheckCircle2 className="w-3 h-3" />
                    Unlocked
                  </span>
                )}
              </div>

              {isUnlocked && <HintContent payload={payload} />}

              {!isUnlocked && (
                <button
                  onClick={() => handleUnlock(level)}
                  disabled={!isAvailable || isLoading}
                  className="inline-flex items-center gap-2 text-white text-[11px] font-mono uppercase tracking-wider px-3 py-1.5 rounded-lg border border-white/20 hover:border-white/40 transition disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : isAvailable ? (
                    <Lightbulb className="w-3 h-3" />
                  ) : (
                    <Lock className="w-3 h-3" />
                  )}
                  {isAvailable ? "Unlock hint" : "Locked"}
                </button>
              )}
            </div>
          );
        })}
      </div>

      {error && (
        <p className="mt-4 text-[11px] font-mono text-yellow-300">{error}</p>
      )}
    </div>
  );
}