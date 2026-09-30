import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  FileCode2,
  ListChecks,
  Lightbulb,
  Target,
  AlertCircle,
  CheckCircle2,
  GitBranch,
  Hash,
  Loader2,
  ArrowLeft,
  Inbox,
} from "lucide-react";
import { getIssueBreakdown } from "../services/api.js";
import { getMatchCriteria, getActiveIssueId } from "../utils/sessions.js";
import HintCard from "../components/HintCard.jsx";

// ---------- Reusable primitives ----------

function SectionCard({ icon: Icon, title, children, glow = "violet" }) {
  const glowColor =
    glow === "cyan"
      ? "shadow-[0_0_40px_-10px_rgba(34,211,238,0.15)]"
      : glow === "green"
      ? "shadow-[0_0_40px_-10px_rgba(34,197,94,0.15)]"
      : "shadow-[0_0_40px_-10px_rgba(139,92,246,0.2)]";

  return (
    <div
      className={`rounded-2xl border border-white/10 bg-transparent p-6 sm:p-7 ${glowColor}`}
    >
      <div className="flex items-center gap-2 mb-4">
        {Icon && <Icon className="w-4 h-4 text-white" />}
        <h2 className="text-xs font-mono tracking-[0.15em] text-white uppercase">
          {title}
        </h2>
      </div>
      {children}
    </div>
  );
}

function TextBlock({ children }) {
  return (
    <p className="text-sm text-white/85 leading-relaxed font-mono">
      {children}
    </p>
  );
}

function BulletList({ items = [] }) {
  if (!items.length) return null;
  return (
    <ul className="space-y-2">
      {items.map((item, i) => (
        <li
          key={i}
          className="flex items-start gap-2 text-sm text-white/85 leading-relaxed font-mono"
        >
          <span className="text-white/40 mt-0.5 select-none">•</span>
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

function NumberedList({ items = [] }) {
  if (!items.length) return null;
  return (
    <ol className="space-y-3">
      {items.map((item, i) => (
        <li key={i} className="flex items-start gap-3">
          <span className="shrink-0 w-6 h-6 rounded-md border border-white/15 bg-transparent grid place-items-center text-[10px] font-mono text-white/70 mt-0.5">
            {String(i + 1).padStart(2, "0")}
          </span>
          <span className="text-sm text-white/85 leading-relaxed font-mono">
            {item}
          </span>
        </li>
      ))}
    </ol>
  );
}

function ChipRow({ items = [], icon: Icon, emptyText }) {
  if (!items.length) {
    if (!emptyText) return null;
    return (
      <p className="text-[12px] font-mono text-white/40 italic">{emptyText}</p>
    );
  }
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item, i) => (
        <span
          key={i}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-mono rounded-lg border border-white/15 text-white/90 hover:border-white/30 transition-colors"
        >
          {Icon && <Icon className="w-3 h-3 text-white/60" />}
          {item}
        </span>
      ))}
    </div>
  );
}

function ContextBadge({ status }) {
  if (!status) return null;
  const map = {
    sufficient: {
      label: "Context Sufficient",
      cls: "border-green-500/40 text-green-300 bg-transparent",
      Icon: CheckCircle2,
    },
    insufficient: {
      label: "Context Insufficient",
      cls: "border-yellow-500/40 text-yellow-300 bg-transparent",
      Icon: AlertCircle,
    },
    partial: {
      label: "Context Partial",
      cls: "border-yellow-500/40 text-yellow-300 bg-transparent",
      Icon: AlertCircle,
    },
  };
  const cfg = map[String(status).toLowerCase()] ?? {
    label: status,
    cls: "border-white/20 text-white/70",
    Icon: AlertCircle,
  };
  const { Icon } = cfg;
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-[7px] border text-[10px] font-mono uppercase tracking-wider ${cfg.cls}`}
    >
      <Icon className="w-3 h-3" />
      {cfg.label}
    </span>
  );
}

// ---------- Main page ----------

export default function IssueDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // If no id in URL, try last viewed issue from localStorage
  const effectiveId = id || getActiveIssueId();

  useEffect(() => {
    let cancelled = false;

    async function load() {
      if (!effectiveId) {
        if (!cancelled) {
          setLoading(false);
          setData(null);
        }
        return;
      }

      const criteria = getMatchCriteria();
      if (!criteria) {
        if (!cancelled) {
          setError("Match criteria missing. Please search for issues first.");
          setLoading(false);
        }
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const json = await getIssueBreakdown({
          issueId: effectiveId,
          repo: criteria.repo,
          skills: criteria.skills,
          experience: criteria.experience,
        });

        if (!cancelled) setData(json);
      } catch (e) {
        if (!cancelled) setError(e.message || "Something went wrong");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [effectiveId]);

  // ---------- Loading ----------
  if (loading) {
    return (
      <div className="min-h-screen pt-32 pb-24 flex items-center justify-center">
        <div className="flex items-center gap-3 text-white/70 font-mono text-sm">
          <Loader2 className="w-4 h-4 animate-spin" />
          Loading issue breakdown…
        </div>
      </div>
    );
  }

  // ---------- No issue selected ----------
  if (!effectiveId && !data && !error) {
    return (
      <div className="min-h-screen pt-32 pb-24">
        <div className="max-w-3xl mx-auto px-5">
          <div className="mb-10 text-center">
            <span className="text-[10px] font-mono tracking-[0.2em] text-white uppercase">
              Contributions
            </span>
            <h1 className="text-4xl md:text-5xl font-extrabold mt-3 tracking-tight text-white">
              No active contribution.
            </h1>
            <p className="text-white mt-3 max-w-2xl mx-auto">
              Pick an issue to start working on it — its breakdown will appear here.
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-transparent p-10 sm:p-14 shadow-[0_0_40px_-10px_rgba(139,92,246,0.2)] text-center">
            <div className="w-14 h-14 mx-auto rounded-2xl border border-white/15 grid place-items-center mb-5">
              <Inbox className="w-6 h-6 text-white/70" />
            </div>
            <h2 className="text-lg font-semibold text-white mb-2">
              Nothing selected
            </h2>
            <p className="text-sm text-white/60 font-mono max-w-md mx-auto">
              Explore issues that match your skills to begin.
            </p>
            <button
              onClick={() => navigate("/match")}
              className="mt-6 inline-flex items-center gap-2 text-white px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-300 border border-[#6d8cff] shadow-[0_0_18px_-4px_rgba(109,140,255,0.55)] hover:shadow-[0_0_26px_-4px_rgba(109,140,255,0.85)] hover:border-[#8aa3ff]"
              style={{
                background:
                  "linear-gradient(to right, rgba(109,140,255,0.12), rgba(109,140,255,0.05))",
              }}
            >
              Explore Issues
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ---------- Error ----------
  if (error) {
    return (
      <div className="min-h-screen pt-32 pb-24">
        <div className="max-w-3xl mx-auto px-5">
          <div className="rounded-2xl border border-red-500/30 bg-transparent p-6 shadow-[0_0_40px_-10px_rgba(239,68,68,0.25)]">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="w-4 h-4 text-red-300" />
              <h2 className="text-xs font-mono tracking-[0.15em] text-red-200 uppercase">
                Failed to load
              </h2>
            </div>
            <p className="text-sm text-white/80 font-mono">{error}</p>
            <div className="mt-5 flex gap-3">
              <button
                onClick={() => navigate(-1)}
                className="inline-flex items-center gap-2 text-white px-5 py-2.5 rounded-xl text-sm font-semibold border border-[#6d8cff] shadow-[0_0_18px_-4px_rgba(109,140,255,0.55)] hover:border-[#8aa3ff] transition-all"
              >
                <ArrowLeft className="w-4 h-4" />
                Go back
              </button>
              <button
                onClick={() => navigate("/match")}
                className="inline-flex items-center gap-2 text-white px-5 py-2.5 rounded-xl text-sm font-semibold border border-white/20 hover:border-white/40 transition-all"
              >
                Search again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ---------- Breakdown render ----------
  const { issue_id, repo, breakdown = {} } = data || {};
  const {
    problem_summary,
    expected_behavior,
    current_behavior,
    confirmed_facts = [],
    files_to_inspect = [],
    relevant_symbols = [],
    concepts_to_understand = [],
    investigation_steps = [],
    verification_target,
    context_status,
  } = breakdown;

  return (
    <div className="min-h-screen pt-32 pb-24">
      <div className="max-w-3xl mx-auto px-5 space-y-6">
        {/* Header */}
        <div>
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-1.5 text-[11px] font-mono text-white/50 hover:text-white transition-colors mb-6"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Back
          </button>

          <div className="flex flex-wrap items-center gap-2 text-[10px] font-mono tracking-[0.15em] text-white/60 uppercase mb-3">
            <GitBranch className="w-3 h-3" />
            <span>{repo}</span>
            <span className="text-white/25">·</span>
            <Hash className="w-3 h-3" />
            <span>{issue_id}</span>
          </div>

          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-white">
            Issue Breakdown
          </h1>

          {context_status && (
            <div className="mt-4">
              <ContextBadge status={context_status} />
            </div>
          )}
        </div>

        {problem_summary && (
          <SectionCard icon={Lightbulb} title="Problem Summary" glow="violet">
            <TextBlock>{problem_summary}</TextBlock>
          </SectionCard>
        )}

        {(expected_behavior || current_behavior) && (
          <div className="grid sm:grid-cols-2 gap-6">
            {expected_behavior && (
              <SectionCard
                icon={CheckCircle2}
                title="Expected Behavior"
                glow="green"
              >
                <TextBlock>{expected_behavior}</TextBlock>
              </SectionCard>
            )}
            {current_behavior && (
              <SectionCard
                icon={AlertCircle}
                title="Current Behavior"
                glow="cyan"
              >
                <TextBlock>{current_behavior}</TextBlock>
              </SectionCard>
            )}
          </div>
        )}

        {confirmed_facts.length > 0 && (
          <SectionCard icon={ListChecks} title="Confirmed Facts">
            <BulletList items={confirmed_facts} />
          </SectionCard>
        )}

        {files_to_inspect.length > 0 && (
          <SectionCard icon={FileCode2} title="Files to Inspect">
            <div className="flex flex-col gap-2">
              {files_to_inspect.map((file, i) => (
                <div
                  key={i}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg border border-white/10 font-mono text-[12px] text-white/90 hover:border-white/20 transition-colors"
                >
                  <FileCode2 className="w-3.5 h-3.5 text-white/50 shrink-0" />
                  <span className="truncate">{file}</span>
                </div>
              ))}
            </div>
          </SectionCard>
        )}

        <SectionCard icon={Hash} title="Relevant Symbols">
          <ChipRow
            items={relevant_symbols}
            icon={Hash}
            emptyText="No specific symbols identified."
          />
        </SectionCard>

        {concepts_to_understand.length > 0 && (
          <SectionCard icon={Lightbulb} title="Concepts to Understand">
            <ChipRow items={concepts_to_understand} />
          </SectionCard>
        )}

        {investigation_steps.length > 0 && (
          <SectionCard icon={ListChecks} title="Investigation Steps">
            <NumberedList items={investigation_steps} />
          </SectionCard>
        )}

        {verification_target && (
          <SectionCard icon={Target} title="Verification Target" glow="green">
            <TextBlock>{verification_target}</TextBlock>
          </SectionCard>
        )}

        {/* Hint panel */}
        <HintCard
          issueId={issue_id ?? effectiveId}
          issueContext={{
            problem_summary,
            files_to_inspect,
            current_behavior,
            expected_behavior,
          }}
          currentProgress={{}}
        />
      </div>
    </div>
  );
}