import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen pt-32 relative overflow-hidden flex flex-col items-center">
      
      {/* Google Font: Orbitron (robotic / futuristic) */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;800;900&display=swap');
      `}</style>

      {/* Background Ambient Glows */}
      <div className="absolute top-0 left-1/4 w-125 h-125 bg-violet-600/10 rounded-full blur-[120px] pointer-events-none -z-10" />
      <div className="absolute top-1/4 right-0 w-100 h-100 bg-cyan-600/10 rounded-full blur-[100px] pointer-events-none -z-10" />

      <div className="max-w-6xl mx-auto px-5 w-full relative z-10 flex flex-col items-center pb-24">
        
        {/* ================= HERO SECTION ================= */}
        <div className="text-center max-w-4xl w-full">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.15 }}
            className="text-4xl sm:text-6xl md:text-7xl font-black uppercase text-white"
            style={{
              fontFamily: "'Orbitron', monospace",
              letterSpacing: "0.25em",
              fontWeight: 900,
              textShadow: `
                0 1px 0 #a78bfa,
                0 2px 0 #8b5cf6,
                0 3px 0 #7c3aed,
                0 4px 0 #6d28d9,
                0 5px 0 #5b21b6,
                0 6px 0 #4c1d95,
                0 8px 12px rgba(139, 92, 246, 0.5),
                0 12px 24px rgba(34, 211, 238, 0.25)
              `,
            }}
          >
            CONTRIBPILOT
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.25 }}
            className="max-w-2xl mx-auto text-slate-300 text-lg leading-relaxed mt-10"
          >
            AI-Powered GitHub contribution assistant
            <br className="hidden sm:block" />
            for issue discovery, breakdown and guided hints.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex justify-center mt-10"
          >
            <button
              onClick={() => navigate("/match")}
              className="flex items-center justify-center gap-2 `bg-linear-to-r`  from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white px-8 py-4 rounded-xl font-semibold transition-all duration-300 shadow-lg shadow-violet-500/20"
            >
              Find My First Issue <ArrowRight className="w-4 h-4" />
            </button>
          </motion.div>
        </div>

      </div>
    </div>
  );
}