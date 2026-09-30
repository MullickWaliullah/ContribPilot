import { useEffect, useState } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { Settings } from "lucide-react";

const STEPS = ["Match", "Understand", "Reproduce", "Fix", "Verify", "PR Ready"];

function stepFromPath(pathname) {
  if (pathname.startsWith("/contrib/issue/")) return 1;
  if (pathname.startsWith("/issue")) return 1;
  if (pathname.startsWith("/pr-ready")) return 5;
  return -1;
}

export default function Navbar({ currentStep, blurOnScroll = false }) {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);

  const derived = currentStep ?? stepFromPath(pathname);

  useEffect(() => {
    if (!blurOnScroll) return;
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [blurOnScroll]);

  const shellClass = [
    "sticky top-0 z-50",
    "bg-transparent",
    blurOnScroll && scrolled
      ? "backdrop-blur-xl border-b border-[#252b3c]"
      : "border-b border-transparent",
    "transition-colors duration-300",
  ].filter(Boolean).join(" ");

  // Base styles for both active and inactive links
  const baseLink = "px-4 py-2 rounded-lg text-xs transition-colors";
  const activeLink = "text-violet-200 bg-[#0d1018]";
  const inactiveLink = "text-slate-400 hover:text-slate-200";

  // Standard NavLink resolver
  const linkClass = ({ isActive }) =>
    [baseLink, isActive ? activeLink : inactiveLink].join(" ");

  // Contributions should stay highlighted on /contrib AND /contrib/issue/:id
  // (and legacy /issue/:id for backward-compat)
  const contributionsActive =
    pathname.startsWith("/contrib") || pathname.startsWith("/issue");

  return (
    <header className={shellClass}>
      <div className="max-w-[1450px] mx-auto px-5 h-[68px] flex items-center justify-between">
        {/* ---------- Logo ---------- */}
        <button
          onClick={() => navigate("/")}
          className="flex items-center gap-3 shrink-0"
          aria-label="ContribPilot home"
        >
          <div className="text-left">
            <b className="text-lg leading-none">ContribPilot</b>
            <div className="mono text-[9px] text-violet-300 tracking-[.22em] mt-1">
              VERIFIED CONTRIBUTION
            </div>
          </div>
        </button>

        {/* ---------- Primary nav ---------- */}
        <nav className="hidden md:flex items-center gap-1 p-1 rounded-xl border border-[#252b3c] bg-transparent">
          <NavLink to="/" end className={linkClass}>
            Home
          </NavLink>
          <NavLink to="/match" className={linkClass}>
            Explore Issues
          </NavLink>

          {/* Contributions — active on /contrib and /contrib/issue/:id */}
          <NavLink
            to="/contrib"
            className={[baseLink, contributionsActive ? activeLink : inactiveLink].join(" ")}
          >
            Contributions
          </NavLink>

          <NavLink to="/config" className={linkClass}>
            Configuration
          </NavLink>
          <NavLink to="/docs" className={linkClass}>
            Docs
          </NavLink>
        </nav>

        {/* ---------- Current contribution step ---------- */}
        {derived >= 0 && (
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg border border-[#30384f] bg-transparent">
            <span className="mono text-[9px] text-slate-500">STEP</span>
            <span className="mono text-[10px] text-violet-300">
              {String(derived + 1).padStart(2, "0")}
            </span>
            <span className="text-xs text-slate-300">{STEPS[derived]}</span>
          </div>
        )}

        {/* ---------- Right cluster ---------- */}
        <div className="flex items-center gap-3">
          <span className="hidden sm:inline-block mono text-[10px] px-2.5 py-1.5 rounded-[7px] border border-green-500/30 text-green-300">
            ● GitHub Connected
          </span>

          <button
            onClick={() => navigate("/config")}
            className={`w-9 h-9 rounded-xl grid place-items-center border transition-colors ${
              pathname.startsWith("/config")
                ? "border-violet-500/60 bg-[#111522]"
                : "border-[#30384f] bg-transparent hover:bg-[#111522]"
            }`}
            aria-label="Settings"
          >
            <Settings
              className={`w-4 h-4 transition-colors ${
                pathname.startsWith("/config") ? "text-violet-300" : "text-slate-300"
              }`}
            />
          </button>

          <div className="w-9 h-9 rounded-full p-px bg-linear-to-br from-violet-500 to-cyan-400">
            <div className="w-full h-full rounded-full bg-[#10131d] grid place-items-center mono text-[10px] text-slate-300">
              DEV
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}