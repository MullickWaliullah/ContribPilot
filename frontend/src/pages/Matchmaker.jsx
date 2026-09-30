import { useState } from "react";
import IssueCard from "../components/IssueCard";

export default function Matchmaker() {
  // This is the state that holds the list of issues
  const [issues, setIssues] = useState([
    {
      id: 42,
      repo: "demo/todo-api",
      title: "Fix whitespace handling when creating a todo",
      labels: ["good first issue", "pytest"],
      language: "Python",
      difficulty: "Beginner",
      matchScore: 94,
      aiReason: "You know Python and pytest. This issue involves basic string manipulation.",
    },
    {
      id: 18,
      repo: "demo/calculator-api",
      title: "Handle empty expression input",
      labels: ["good first issue"],
      language: "Python",
      difficulty: "Intermediate",
      matchScore: 89,
      aiReason: "Matches your Python skills. Focuses on input validation and error handling.",
    }
  ]);

  return (
    <div className="min-h-screen pt-32 pb-24">
      <div className="max-w-6xl mx-auto px-5">
        
        {/* Page Header */}
        <div className="mb-10">
          <span className="text-[10px] font-mono tracking-[0.2em] text-violet-300 uppercase">
            Issue Matchmaker
          </span>
          <h1 className="text-4xl md:text-5xl font-extrabold mt-3 tracking-tight text-white">
            Find an issue worth solving.
          </h1>
          <p className="text-slate-400 mt-3 max-w-2xl">
            Tell ContribPilot what you know. We'll surface issues that fit your skills.
          </p>
        </div>

        {/* The Results List */}
        <div className="space-y-4 mt-8">
          <h2 className="text-xl font-bold text-white mb-4">Recommended for you</h2>
          {issues.map((issue) => (
            <IssueCard key={issue.id} issue={issue} />
          ))}
        </div>

      </div>
    </div>
  );
}