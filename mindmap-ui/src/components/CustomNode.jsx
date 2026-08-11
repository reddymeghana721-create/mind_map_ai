import React, { memo } from "react";
import { Handle, Position } from "@xyflow/react";
import { motion } from "framer-motion";
import { ChevronRight, ChevronDown } from "lucide-react";

function CustomNode({ data }) {
  const {
    id,
    label,
    depth,
    hasChildren,
    isExpanded,
    isSelected,
    isInActivePath
  } = data;

  const handleToggle = (e) => {
    e.stopPropagation();
    if (data.onToggle) {
      data.onToggle(id);
    }
  };

  return (
    <motion.div
      initial={{ scale: 0.96, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.15 }}
      className={`relative group cursor-pointer select-none rounded-xl px-3 py-2.5 w-[210px] transition-all duration-150 ${
        isSelected
          ? "bg-slate-900 border-2 border-sky-400 text-slate-100 shadow-md shadow-sky-500/10"
          : isInActivePath
          ? "bg-slate-900/90 border border-sky-500/50 text-slate-200"
          : "bg-slate-900/80 border border-slate-800 text-slate-300 hover:border-slate-700 hover:text-slate-100"
      }`}
    >
      {/* Target Handle (Left) */}
      {depth > 0 && (
        <Handle
          type="target"
          position={Position.Left}
          className="!w-2 !h-2 !bg-slate-950 !border !border-sky-400 opacity-60 group-hover:opacity-100"
        />
      )}

      {/* Node Main Content: Title & Small Arrow Only */}
      <div className="flex items-center justify-between gap-2">
        <h3 className="text-xs font-medium leading-snug line-clamp-2">
          {label}
        </h3>

        {hasChildren && (
          <button
            onClick={handleToggle}
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors shrink-0"
            title={isExpanded ? "Collapse" : "Expand"}
          >
            {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
          </button>
        )}
      </div>

      {/* Source Handle (Right) */}
      {hasChildren && (
        <Handle
          type="source"
          position={Position.Right}
          className="!w-2 !h-2 !bg-slate-950 !border !border-sky-400 opacity-60 group-hover:opacity-100"
        />
      )}
    </motion.div>
  );
}

export default memo(CustomNode);
