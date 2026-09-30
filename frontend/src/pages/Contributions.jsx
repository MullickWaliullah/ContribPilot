import { useNavigate } from "react-router-dom";
import { Inbox, Plus } from "lucide-react";

export default function Contributions() {
  const navigate = useNavigate();

  // TODO: backend se user ki started contributions laao
  // Abhi khaali list — empty state dikhega
  const contributions = [];

  return (
    <div className="min-h-screen pt-32 pb-24">
      <div className="max-w-3xl mx-auto px-5">

        {/* ---------- Page Header ---------- */}
        <div className="mb-10 text-center">
          <span className="text-[10px] font-mono tracking-[0.2em] text-white uppercase">
            Contributions
          </span>
          <h1 className="text-4xl md:text-5xl font-extrabold mt-3 tracking-tight text-white">
            Your contribution workspace.
          </h1>
          <p className="text-white mt-3 max-w-2xl mx-auto">
            Issues you've started working on will appear here.
          </p>
        </div>

        {/* ---------- Empty State ---------- */}
        {contributions.length === 0 ? (
          <div className="rounded-2xl border border-white/10 bg-transparent p-10 sm:p-14 shadow-[0_0_40px_-10px_rgba(139,92,246,0.2)] text-center">
            <div className="w-14 h-14 mx-auto rounded-2xl border border-white/15 grid place-items-center mb-5">
              <Inbox className="w-6 h-6 text-white/70" />
            </div>

            <h2 className="text-lg font-semibold text-white mb-2">
              No contributions yet
            </h2>

            <p className="text-sm text-white/60 font-mono max-w-md mx-auto">
              Start by exploring issues that match your skills.
            </p>

            <button
              onClick={() => navigate("/match")}
              className="mt-6 inline-flex items-center gap-2 text-white px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-300 border border-[#6d8cff] shadow-[0_0_18px_-4px_rgba(109,140,255,0.55)] hover:shadow-[0_0_26px_-4px_rgba(109,140,255,0.85)] hover:border-[#8aa3ff]"
              style={{
                background:
                  "linear-gradient(to right, rgba(109,140,255,0.12), rgba(109,140,255,0.05))",
              }}
            >
              <Plus className="w-4 h-4" />
              Find an issue
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Baad me: contributions.map(c => <ContributionRow ... />) */}
          </div>
        )}

      </div>
    </div>
  );
}