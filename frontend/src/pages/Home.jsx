import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen pt-32 relative overflow-hidden flex flex-col items-center">
      
      {/* Background Ambient Glows */}
      <div className="absolute top-0 left-1/4 w-125 h-125 bg-violet-600/10 rounded-full blur-[120px] pointer-events-none -z-10" />
      <div className="absolute top-1/4 right-0 w-100 h-100 bg-cyan-600/10 rounded-full blur-[100px] pointer-events-none -z-10" />

      <div className="max-w-6xl mx-auto px-5 w-full relative z-10 flex flex-col items-center pb-24">
        
        {/* ================= HERO SECTION ================= */}
        <div className="text-center max-w-4xl w-full">
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="max-w-2xl mx-auto text-slate-300 text-lg leading-relaxed mt-7"
          >
            Find the right GitHub issue, understand unfamiliar code, reproduce the bug, learn the fix, and verify your contribution before opening a PR.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row justify-center gap-4 mt-10"
          >
            <button
              onClick={() => navigate("/match")}
              className="flex items-center justify-center gap-2 `bg-linear-to-r`  from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white px-8 py-4 rounded-xl font-semibold transition-all duration-300 shadow-lg shadow-violet-500/20"
            >
              Find My First Issue <ArrowRight className="w-4 h-4" />
            </button>
            
            <button
              onClick={() => navigate("/workspace")}
              className="flex items-center justify-center gap-2 border border-white/20 hover:bg-white/5 text-white px-8 py-4 rounded-xl font-semibold transition-all duration-300"
            >
              See Workspace
            </button>
          </motion.div>
        </div>

        {/* ================= MOCK TERMINAL CARD ================= */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-16 w-full max-w-4xl rounded-2xl border border-white/10 bg-[#090c14]/80 backdrop-blur-md overflow-hidden shadow-2xl relative z-20"
        >
          {/* Header */}
          <div className="h-12 border-b border-white/10 flex justify-between items-center px-6 bg-white/5">
            <span className="font-mono text-xs text-slate-500">contribpilot / verification</span>
            <span className="px-2.5 py-1 rounded text-[10px] font-mono text-green-400 border border-green-500/30">
              SANDBOX READY
            </span>
          </div>

          {/* Body */}
          <div className="p-8">
            <span className="font-mono text-[10px] text-violet-400 tracking-wider uppercase">Issue #42</span>
            <h2 className="text-2xl md:text-3xl font-bold mt-3 text-white tracking-tight">
              Fix whitespace handling when creating a todo
            </h2>
            
            {/* Tags */}
            <div className="flex flex-wrap gap-3 mt-6">
              <span className="px-3 py-1.5 text-xs tracking-wide rounded-md border border-white/10 text-slate-300 bg-white/5">python</span>
              <span className="px-3 py-1.5 text-xs tracking-wide rounded-md border border-white/10 text-slate-300 bg-white/5">pytest</span>
              <span className="px-3 py-1.5 text-xs tracking-wide rounded-md border border-green-500/20 text-green-400/90 bg-green-500/5">good first issue</span>
            </div>

            {/* Skill Match Linear Bar */}
            <div className="mt-12">
              <div className="flex justify-between items-end mb-3">
                <span className="text-slate-400 text-sm">Skill Match</span>
                <span className="text-green-400 font-bold text-lg leading-none">94%</span>
              </div>
              <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                <div className="h-full w-[94%] `bg-linear-to-r` from-indigo-500 via-violet-500 to-cyan-400 rounded-full" />
              </div>
            </div>

            {/* Verification Loop */}
            <div className="mt-12 pt-8 border-t border-white/10">
              <span className="font-mono text-[10px] text-violet-400 tracking-wider uppercase">Verification Loop</span>
              
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between sm:text-center mt-6 font-mono text-xs gap-4 sm:gap-0">
                <div className="flex sm:flex-col items-center gap-3 sm:gap-1">
                  <span className="text-slate-500">01</span>
                  <span className="text-white">Discover</span>
                </div>
                <ArrowRight className="hidden sm:block w-4 h-4 text-slate-600" />
                
                <div className="flex sm:flex-col items-center gap-3 sm:gap-1">
                  <span className="text-slate-500">02</span>
                  <span className="text-white">Understand</span>
                </div>
                <ArrowRight className="hidden sm:block w-4 h-4 text-slate-600" />
                
                <div className="flex sm:flex-col items-center gap-3 sm:gap-1">
                  <span className="text-slate-500">03</span>
                  <span className="text-white">Verify</span>
                </div>
              </div>
            </div>

          </div>
        </motion.div>
      </div>
    </div>
  );
}