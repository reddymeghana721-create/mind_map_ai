import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  X,
  FileText,
  Image as ImageIcon,
  Edit3,
  HelpCircle,
  Sparkles,
  CheckCircle2,
  Play,
  RotateCcw,
  BookOpen
} from "lucide-react";

export default function LearningPanel({ selectedNode, onClose }) {
  const [activeTab, setActiveTab] = useState("summary");
  const [isVideoLoading, setIsVideoLoading] = useState(true);
  const [userNote, setUserNote] = useState("");
  const [isNoteSaved, setIsNoteSaved] = useState(false);
  const [quizAnswers, setQuizAnswers] = useState({});
  const [quizSubmitted, setQuizSubmitted] = useState(false);

  useEffect(() => {
    if (selectedNode) {
      setIsVideoLoading(true);
      setActiveTab("summary");
      setUserNote(localStorage.getItem(`note_${selectedNode.id}`) || "");
      setQuizAnswers({});
      setQuizSubmitted(false);
    }
  }, [selectedNode]);

  if (!selectedNode) return null;

  const videoUrl = selectedNode.video
    ? selectedNode.video.startsWith("http")
      ? selectedNode.video
      : `http://localhost:5000${selectedNode.video}`
    : null;

  const handleSaveNote = () => {
    localStorage.setItem(`note_${selectedNode.id}`, userNote);
    setIsNoteSaved(true);
    setTimeout(() => setIsNoteSaved(false), 2000);
  };

  const sampleQuiz = [
    {
      id: 1,
      question: `What is the core concept presented in ${selectedNode.label}?`,
      options: [
        "Movement of charge / concentration principle",
        "Total energy dissipation in medium",
        "Static equilibrium without change",
        "Thermal radiation in closed boundaries"
      ],
      correct: 0
    },
    {
      id: 2,
      question: "Which indicator or law helps test this physical property?",
      options: [
        "Newton's Law of Inertia",
        "Right-Hand Thumb Rule / Litmus Indicator",
        "Boyle's Ideal Gas Law",
        "Ohm's Constant Resistance"
      ],
      correct: 1
    },
    {
      id: 3,
      question: "What outcome occurs when concentration/current is doubled?",
      options: [
        "Field strength or yield increases proportionally",
        "Output drops to absolute zero",
        "Inverse square compression occurs",
        "No observable change"
      ],
      correct: 0
    }
  ];

  const calculateScore = () => {
    let score = 0;
    sampleQuiz.forEach((q) => {
      if (quizAnswers[q.id] === q.correct) score += 1;
    });
    return score;
  };

  return (
    <motion.aside
      initial={{ x: "100%", opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: "100%", opacity: 0 }}
      transition={{ duration: 0.2, ease: "easeInOut" }}
      className="fixed right-0 top-0 bottom-0 w-[540px] max-w-[50vw] bg-slate-950 border-l border-slate-800/80 z-30 flex flex-col shadow-2xl overflow-hidden select-none"
    >
      {/* 1. MINIMAL TOP BAR (CLOSE BUTTON ONLY) */}
      <div className="flex items-center justify-end p-4">
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900 transition-all"
          title="Close panel"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* 2. MAIN LEARNING CONTENT (TITLE + VIDEO + TABS) */}
      <div className="flex-1 overflow-y-auto px-6 pb-6 space-y-5">
        {/* PRIMARY CONCEPT TITLE */}
        <h1 className="text-xl font-bold text-slate-100 leading-snug tracking-tight">
          {selectedNode.label}
        </h1>

        {/* PROMINENT 16:9 VIDEO PLAYER */}
        <div className="relative w-full aspect-video rounded-xl overflow-hidden bg-black border border-slate-800 flex items-center justify-center">
          {videoUrl ? (
            <>
              {isVideoLoading && (
                <div className="absolute inset-0 z-10 animate-shimmer flex flex-col items-center justify-center gap-2 text-slate-400">
                  <Play className="w-8 h-8 text-sky-400/70 animate-pulse" />
                  <span className="text-xs font-medium">Loading Video...</span>
                </div>
              )}

              <video
                key={videoUrl}
                controls
                autoPlay={false}
                onLoadedData={() => setIsVideoLoading(false)}
                className="w-full h-full object-contain z-20"
                src={videoUrl}
              >
                Your browser does not support HTML5 video playback.
              </video>
            </>
          ) : (
            <div className="p-6 text-center space-y-2">
              <div className="w-10 h-10 rounded-xl bg-slate-900 border border-slate-800 text-sky-400 flex items-center justify-center mx-auto">
                <BookOpen className="w-5 h-5" />
              </div>
              <h4 className="text-xs font-semibold text-slate-200">Textbook Reading Module</h4>
              <p className="text-[11px] text-slate-400 max-w-[280px] mx-auto">
                No video recording for this topic. Read the textbook summary below.
              </p>
            </div>
          )}
        </div>

        {/* MINIMAL TABS BELOW VIDEO */}
        <div className="flex items-center gap-2 border-b border-slate-800/80 pb-2 text-xs">
          {[
            { id: "summary", label: "Summary", icon: FileText },
            { id: "notes", label: "Notes", icon: Edit3 },
            { id: "images", label: "Diagrams", icon: ImageIcon },
            { id: "quiz", label: "Quiz", icon: HelpCircle }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition-all ${
                  isActive
                    ? "bg-sky-500/10 text-sky-400 border border-sky-500/20"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* TAB CONTENTS */}
        <div className="pt-1">
          {/* TAB: SUMMARY */}
          {activeTab === "summary" && (
            <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 whitespace-pre-line text-slate-200 leading-normal">
                {selectedNode.summary}
              </div>
            </div>
          )}

          {/* TAB: NOTES */}
          {activeTab === "notes" && (
            <div className="space-y-2.5 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-300">Personal Notes</span>
                {isNoteSaved && (
                  <span className="text-emerald-400 flex items-center gap-1 text-[11px]">
                    <CheckCircle2 className="w-3 h-3" /> Saved
                  </span>
                )}
              </div>
              <textarea
                rows={5}
                value={userNote}
                onChange={(e) => setUserNote(e.target.value)}
                placeholder="Type your notes or key points here..."
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500/50"
              />
              <button
                onClick={handleSaveNote}
                className="w-full py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-white font-semibold text-xs transition-all"
              >
                Save Notes
              </button>
            </div>
          )}

          {/* TAB: DIAGRAMS */}
          {activeTab === "images" && (
            <div className="space-y-2.5">
              <span className="text-xs font-semibold text-slate-300 block">Illustrations</span>
              <div className="grid grid-cols-2 gap-2.5">
                {[1, 2].map((idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center space-y-2 cursor-pointer hover:border-sky-500/40 transition-all"
                  >
                    <div className="w-full h-20 rounded-lg bg-slate-800/50 flex items-center justify-center text-slate-500">
                      <ImageIcon className="w-6 h-6" />
                    </div>
                    <span className="text-[11px] text-slate-300 block">Figure {idx}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB: QUIZ */}
          {activeTab === "quiz" && (
            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between font-semibold text-slate-300">
                <span>Self Assessment</span>
                <span className="text-sky-400">3 Questions</span>
              </div>

              {!quizSubmitted ? (
                <div className="space-y-3">
                  {sampleQuiz.map((q) => (
                    <div key={q.id} className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                      <p className="font-semibold text-slate-200">
                        {q.id}. {q.question}
                      </p>
                      <div className="space-y-1">
                        {q.options.map((opt, optIdx) => (
                          <button
                            key={optIdx}
                            onClick={() => setQuizAnswers({ ...quizAnswers, [q.id]: optIdx })}
                            className={`w-full text-left p-2 rounded-lg text-xs transition-all border ${
                              quizAnswers[q.id] === optIdx
                                ? "bg-sky-500/20 border-sky-500 text-sky-300"
                                : "bg-slate-800/40 border-slate-800/80 text-slate-400 hover:bg-slate-800"
                            }`}
                          >
                            {opt}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}

                  <button
                    onClick={() => setQuizSubmitted(true)}
                    className="w-full py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-white font-semibold text-xs transition-all"
                  >
                    Submit Answers
                  </button>
                </div>
              ) : (
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center space-y-2">
                  <h3 className="font-bold text-slate-100 text-sm">Quiz Result</h3>
                  <p className="text-xs text-slate-400">
                    You scored <span className="text-emerald-400 font-bold">{calculateScore()} / {sampleQuiz.length}</span>.
                  </p>
                  <button
                    onClick={() => setQuizSubmitted(false)}
                    className="flex items-center gap-1 mx-auto px-3 py-1.5 rounded-lg bg-slate-800 text-slate-200 text-xs font-medium hover:bg-slate-700 transition-all"
                  >
                    <RotateCcw className="w-3 h-3" /> Retake
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </motion.aside>
  );
}
