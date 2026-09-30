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

import {
  getMatchCriteria,
  getActiveIssueId,
} from "../utils/sessions.js";

import HintCard from "../components/HintCard.jsx";

function SectionCard({
  icon: Icon,
  title,
  children,
  glow = "violet",
}) {
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
      <div className="flex items-center gap-2.5 mb-5">
        {Icon && (
          <Icon className="w-4 h-4 text-white/80" />
        )}

        <h2 className="text-sm font-mono tracking-[0.12em] text-white uppercase font-semibold">
          {title}
        </h2>
      </div>

      {children}
    </div>
  );
}

function TextBlock({ children }) {
  return (
    <p className="text-[15px] sm:text-base text-white/85 leading-7 font-mono whitespace-pre-wrap break-words">
      {children}
    </p>
  );
}

function BulletList({ items = [] }) {
  if (!items.length) return null;

  return (
    <ul className="space-y-3">
      {items.map((item, i) => (
        <li
          key={i}
          className="flex items-start gap-3 text-[15px] sm:text-base text-white/85 leading-7 font-mono"
        >
          <span className="text-white/40 mt-1 select-none shrink-0">
            •
          </span>

          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

function NumberedList({ items = [] }) {
  if (!items.length) return null;

  return (
    <ol className="space-y-4">
      {items.map((item, i) => (
        <li
          key={i}
          className="flex items-start gap-3"
        >
          <span className="shrink-0 w-7 h-7 rounded-md border border-white/15 bg-transparent grid place-items-center text-[11px] font-mono text-white/70 mt-0.5">
            {String(i + 1).padStart(2, "0")}
          </span>

          <span className="text-[15px] sm:text-base text-white/85 leading-7 font-mono">
            {item}
          </span>
        </li>
      ))}
    </ol>
  );
}

function ChipRow({
  items = [],
  icon: Icon,
  emptyText,
}) {
  if (!items.length) {
    if (!emptyText) return null;

    return (
      <p className="text-[13px] font-mono text-white/40 italic">
        {emptyText}
      </p>
    );
  }

  return (
    <div className="flex flex-wrap gap-2.5">
      {items.map((item, i) => (
        <span
          key={i}
          className="inline-flex items-center gap-1.5 px-3 py-2 text-[12px] font-mono rounded-lg border border-white/15 text-white/90 hover:border-white/30 transition-colors"
        >
          {Icon && (
            <Icon className="w-3 h-3 text-white/60" />
          )}

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

  const cfg =
    map[String(status).toLowerCase()] ?? {
      label: status,
      cls: "border-white/20 text-white/70",
      Icon: AlertCircle,
    };

  const { Icon } = cfg;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-[7px] border text-[11px] font-mono uppercase tracking-wider ${cfg.cls}`}
    >
      <Icon className="w-3 h-3" />
      {cfg.label}
    </span>
  );
}

export default function IssueDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const effectiveId =
    id || getActiveIssueId();

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
          setError(
            "Match criteria missing. Please search for issues first."
          );

          setLoading(false);
        }

        return;
      }

      try {
        setLoading(true);
        setError(null);

        const json =
          await getIssueBreakdown({
            issueId: effectiveId,
            repo: criteria.repo,
            skills: criteria.skills,
            experience: criteria.experience,
          });

        if (!cancelled) {
          setData(json);
        }
      } catch (e) {
        if (!cancelled) {
          setError(
            e?.message ||
              "Something went wrong"
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [effectiveId]);

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

  if (!effectiveId && !data && !error) {
    return (
      <div className="min-h-screen pt-32 pb-24">
        <div className="max-w-3xl mx-auto px-5">
          <div className="mb-10 text-center">
            <span className="text-[11px] font-mono tracking-[0.2em] text-white uppercase">
              Contributions
            </span>

            <h1 className="text-4xl md:text-5xl font-extrabold mt-3 tracking-tight text-white">
              No active contribution.
            </h1>

            <p className="text-white/80 mt-3 max-w-2xl mx-auto text-[15px] leading-7">
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

            <p className="text-sm text-white/60 font-mono max-w-md mx-auto leading-6">
              Explore issues that match your skills to begin.
            </p>

            <button
              onClick={() =>
                navigate("/match")
              }
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

  if (error) {
    return (
      <div className="min-h-screen pt-32 pb-24">
        <div className="max-w-3xl mx-auto px-5">
          <div className="rounded-2xl border border-red-500/30 bg-transparent p-6 shadow-[0_0_40px_-10px_rgba(239,68,68,0.25)]">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="w-4 h-4 text-red-300" />

              <h2 className="text-sm font-mono tracking-[0.15em] text-red-200 uppercase">
                Failed to load
              </h2>
            </div>

            <p className="text-[14px] text-white/80 font-mono leading-6">
              {error}
            </p>

            <div className="mt-5 flex gap-3">
              <button
                onClick={() =>
                  navigate(-1)
                }
                className="inline-flex items-center gap-2 text-white px-5 py-2.5 rounded-xl text-sm font-semibold border border-[#6d8cff] shadow-[0_0_18px_-4px_rgba(109,140,255,0.55)] hover:border-[#8aa3ff] transition-all"
              >
                <ArrowLeft className="w-4 h-4" />
                Go back
              </button>

              <button
                onClick={() =>
                  navigate("/match")
                }
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

  const responseData = data || {};

  const breakdown =
    responseData.breakdown || {};

  const issueData =
    responseData.issue || {};

  const title =
    breakdown.title ||
    issueData.title ||
    responseData.title ||
    "";

  const body =
    breakdown.body ||
    issueData.body ||
    responseData.body ||
    "";

  const language =
    breakdown.language ||
    issueData.language ||
    responseData.language ||
    "";

  const labels =
    breakdown.labels ||
    issueData.labels ||
    responseData.labels ||
    [];

  const repo =
    responseData.repo ||
    breakdown.repo ||
    issueData.repo ||
    "";

  const issue_id =
    responseData.issue_id ||
    breakdown.issue_id ||
    issueData.issue_id ||
    effectiveId;

  const primary_entry_point =
    breakdown.primary_entry_point ||
    issueData.primary_entry_point ||
    responseData.primary_entry_point ||
    "";

  const problem_summary =
    breakdown.problem_summary || "";

  const confirmed_facts =
    Array.isArray(
      breakdown.confirmed_facts
    )
      ? breakdown.confirmed_facts
      : [];

  const files_to_inspect =
    Array.isArray(
      breakdown.files_to_inspect
    )
      ? breakdown.files_to_inspect
      : [];

  const relevant_symbols =
    Array.isArray(
      breakdown.relevant_symbols
    )
      ? breakdown.relevant_symbols
      : [];

  const concepts_to_understand =
    Array.isArray(
      breakdown.concepts_to_understand
    )
      ? breakdown.concepts_to_understand
      : [];

  const investigation_steps =
    Array.isArray(
      breakdown.investigation_steps
    )
      ? breakdown.investigation_steps
      : [];

  const verification_target =
    breakdown.verification_target || "";

  const context_status =
    breakdown.context_status || "";

  const issueContext = {
    repo,
    issue_id,
    title,
    body,
    labels,
    language,
    primary_entry_point,
    problem_summary,
    confirmed_facts,
    files_to_inspect,
    relevant_symbols,
    concepts_to_understand,
    investigation_steps,
    verification_target,
    context_status,
  };

  return (
    <div className="min-h-screen pt-32 pb-24">
      <div className="max-w-3xl mx-auto px-5 space-y-6">

        <div>
          <button
            onClick={() =>
              navigate(-1)
            }
            className="inline-flex items-center gap-1.5 text-[12px] font-mono text-white/55 hover:text-white transition-colors mb-6"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Back
          </button>

          <div className="flex flex-wrap items-center gap-2 text-[11px] font-mono tracking-[0.13em] text-white/60 uppercase mb-3">
            <GitBranch className="w-3.5 h-3.5" />

            <span className="text-white/75">
              {repo}
            </span>

            <span className="text-white/25">
              ·
            </span>

            <Hash className="w-3.5 h-3.5" />

            <span className="text-white/65">
              {issue_id}
            </span>
          </div>

          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-white">
            Issue Breakdown
          </h1>

          {title && (
            <p className="mt-3 text-[15px] sm:text-base text-white/65 font-mono leading-7">
              {title}
            </p>
          )}

          {context_status && (
            <div className="mt-4">
              <ContextBadge
                status={context_status}
              />
            </div>
          )}
        </div>

        {problem_summary && (
          <SectionCard
            icon={Lightbulb}
            title="Problem Summary"
            glow="violet"
          >
            <TextBlock>
              {problem_summary}
            </TextBlock>
          </SectionCard>
        )}

        {confirmed_facts.length > 0 && (
          <SectionCard
            icon={ListChecks}
            title="Confirmed Facts"
          >
            <BulletList
              items={confirmed_facts}
            />
          </SectionCard>
        )}

        {files_to_inspect.length > 0 && (
          <SectionCard
            icon={FileCode2}
            title="Files to Inspect"
          >
            <div className="flex flex-col gap-2.5">
              {files_to_inspect.map(
                (file, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2.5 px-3.5 py-2.5 rounded-lg border border-white/10 font-mono text-[13px] text-white/90 hover:border-white/20 transition-colors"
                  >
                    <FileCode2 className="w-3.5 h-3.5 text-white/50 shrink-0" />

                    <span className="truncate">
                      {file}
                    </span>
                  </div>
                )
              )}
            </div>
          </SectionCard>
        )}

        <SectionCard
          icon={Hash}
          title="Relevant Symbols"
        >
          <ChipRow
            items={relevant_symbols}
            icon={Hash}
            emptyText="No specific symbols identified."
          />
        </SectionCard>

        {concepts_to_understand.length > 0 && (
          <SectionCard
            icon={Lightbulb}
            title="Concepts to Understand"
          >
            <ChipRow
              items={
                concepts_to_understand
              }
            />
          </SectionCard>
        )}

        {investigation_steps.length > 0 && (
          <SectionCard
            icon={ListChecks}
            title="Investigation Steps"
          >
            <NumberedList
              items={
                investigation_steps
              }
            />
          </SectionCard>
        )}

        {verification_target && (
          <SectionCard
            icon={Target}
            title="Verification Target"
            glow="green"
          >
            <TextBlock>
              {verification_target}
            </TextBlock>
          </SectionCard>
        )}

        <HintCard
          key={`hint-${issue_id}`}
          issueId={issue_id}
          issueContext={issueContext}
          currentProgress={{}}
        />

      </div>
    </div>
  );
}