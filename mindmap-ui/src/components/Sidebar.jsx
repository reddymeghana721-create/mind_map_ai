import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  BookOpen,
  Search,
  ChevronLeft,
  ChevronRight,
  Compass,
  Award,
  Sparkles,
  Layers,
  GraduationCap,
  X
} from "lucide-react";

export default function Sidebar({
  mindmaps,
  selectedMindmap,
  onSelectMindmap,
  isCollapsed,
  onToggleCollapse
}) {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredMindmaps = (mindmaps || []).filter((item) => {
    const q = searchTerm.toLowerCase();
    return (
      item.chapter.toLowerCase().includes(q) ||
      item.subject.toLowerCase().includes(q) ||
      item.class_name.toLowerCase().includes(q)
    );
  });

  return (
    <motion.aside
      initial={false}
      animate={{ width: isCollapsed ? "60px" : "260px" }}
      transition={{ duration: 0.2, ease: "easeInOut" }}
      className="relative flex flex-col h-full bg-slate-950 border-r border-slate-800/80 z-20 shrink-0 select-none overflow-hidden"
    >
      {/* Sidebar Header */}
      <div className="flex items-center justify-between p-3 border-b border-slate-800/80">
        {!isCollapsed && (
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h1 className="text-xs font-bold tracking-tight text-slate-100 flex items-center gap-1">
                <span>MindMap</span>
                <span className="text-[10px] font-semibold px-1.5 py-0.2 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
                  AI
                </span>
              </h1>
            </div>
          </div>
        )}

        <button
          onClick={onToggleCollapse}
          className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-sky-400 transition-all mx-auto"
          title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Expanded Sidebar Body */}
      <AnimatePresence>
        {!isCollapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex-1 flex flex-col min-h-0"
          >
            {/* Search Input */}
            <div className="p-3 border-b border-slate-800/50">
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search courses..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-7 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500/50 transition-all"
                />
                {searchTerm && (
                  <button
                    onClick={() => setSearchTerm("")}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </div>
            </div>

            {/* Course List */}
            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              <div className="flex items-center justify-between text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-1">
                <span>Courses</span>
                <span className="text-slate-500">{filteredMindmaps.length}</span>
              </div>

              <div className="space-y-1.5">
                {filteredMindmaps.map((item, idx) => {
                  const isSelected =
                    selectedMindmap &&
                    selectedMindmap.class_name === item.class_name &&
                    selectedMindmap.subject === item.subject &&
                    selectedMindmap.chapter === item.chapter;

                  return (
                    <div
                      key={idx}
                      onClick={() => onSelectMindmap(item)}
                      className={`p-2.5 rounded-lg cursor-pointer transition-all border ${
                        isSelected
                          ? "bg-slate-900 border-sky-500/70 text-slate-100"
                          : "bg-slate-900/40 border-slate-800/60 text-slate-300 hover:bg-slate-900 hover:border-slate-700"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-0.5">
                        <span className="text-[9px] font-semibold text-sky-400 uppercase tracking-wider">
                          {item.class_name} · {item.subject}
                        </span>
                        {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-sky-400" />}
                      </div>
                      <h4 className="text-xs font-semibold line-clamp-1">
                        {item.chapter.replace(/_/g, " ")}
                      </h4>
                    </div>
                  );
                })}

                {filteredMindmaps.length === 0 && (
                  <div className="text-center py-6 text-xs text-slate-500">
                    No courses found.
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Collapsed Icon Bar */}
      {isCollapsed && (
        <div className="flex-1 flex flex-col items-center py-4 gap-4 text-slate-400">
          <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20">
            <BookOpen className="w-4 h-4" />
          </div>
          <div className="p-2 rounded-lg bg-slate-900 text-slate-400 border border-slate-800 hover:text-sky-400">
            <Layers className="w-4 h-4" />
          </div>
        </div>
      )}
    </motion.aside>
  );
}
