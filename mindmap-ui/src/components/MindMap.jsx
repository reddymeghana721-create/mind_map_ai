import React, { useState, useMemo, useCallback, useRef, useEffect } from "react";
import "./MindMap.css";

// ---- Layout constants ----
const COLUMN_WIDTH = 260;
const ROW_HEIGHT = 84;      // increased spacing so wrapped labels never overlap the next node
const NODE_WIDTH = 200;
const NODE_HEIGHT = 64;     // fixed height that fits 2 wrapped lines of label text
const PADDING = 40;

// ---- Branch color palette, keyed by icon of the depth-1 ancestor ----
const BRANCH_COLORS = {
  apple:  { bg: "#1e3a2f", border: "#2f5c47", accent: "#5fd8a0", line: "#3f7a5c" }, // Nutrition
  bolt:   { bg: "#3a2a12", border: "#5c4419", accent: "#f0b34c", line: "#7a5c26" }, // Respiration
  circle: { bg: "#16233a", border: "#254068", accent: "#6fa8ff", line: "#2f4f7a" }, // Transportation / generic
  filter: { bg: "#2a1c3a", border: "#452a5c", accent: "#c98cf0", line: "#5c3a7a" }, // Excretion
  default:{ bg: "#20202a", border: "#33333f", accent: "#9fa3b0", line: "#3a3a48" },
};
const ROOT_COLOR = { bg: "#2f2d55", border: "#4b4890", accent: "#a8a4f0", line: "#4b4890" };

function colorFor(icon) {
  return BRANCH_COLORS[icon] || BRANCH_COLORS.default;
}

function layoutTree(root, expanded) {
  const positioned = [];
  const edges = [];
  const counter = { n: 0 };

  function visit(node, depth, branchIcon) {
    const isRoot = depth === 0;
    const currentBranchIcon = depth === 1 ? node.ui?.icon : branchIcon;
    const isExpanded = expanded.has(node.id);
    const hasChildren = node.children && node.children.length > 0;

    let y;
    if (hasChildren && isExpanded) {
      const childYs = node.children.map((child) =>
        visit(child, depth + 1, currentBranchIcon)
      );
      y = (childYs[0] + childYs[childYs.length - 1]) / 2;
      node.children.forEach((child) => {
        edges.push({
          from: { x: depth * COLUMN_WIDTH + NODE_WIDTH, y },
          to: { x: (depth + 1) * COLUMN_WIDTH, y: child._y },
          color: isRoot ? ROOT_COLOR.line : colorFor(currentBranchIcon).line,
        });
      });
    } else {
      y = counter.n * ROW_HEIGHT;
      counter.n += 1;
    }

    node._y = y;
    positioned.push({
      id: node.id,
      label: node.label,
      summary: node.summary,
      children: node.children,
      x: depth * COLUMN_WIDTH,
      y,
      hasChildren,
      isExpanded,
      depth,
      color: isRoot ? ROOT_COLOR : colorFor(currentBranchIcon),
    });
    return y;
  }

  visit(root, 0, null);
  return { positioned, edges };
}

function bezierPath(from, to) {
  const dx = Math.max(40, (to.x - from.x) / 2);
  return `M ${from.x},${from.y} C ${from.x + dx},${from.y} ${to.x - dx},${to.y} ${to.x},${to.y}`;
}

export default function MindMap({ data }) {
  const [expanded, setExpanded] = useState(() => new Set([data.id]));
  const [selectedNode, setSelectedNode] = useState(data);

  const scrollRef = useRef(null);
  // plain ref (not state) so dragging never triggers re-renders — keeps panning smooth
  const drag = useRef({ active: false, startX: 0, startY: 0, scrollLeft: 0, scrollTop: 0, moved: false });

  const handleMouseDown = useCallback((e) => {
    if (e.button !== 0) return; // left click only
    const el = scrollRef.current;
    drag.current = {
      active: true,
      startX: e.pageX,
      startY: e.pageY,
      scrollLeft: el.scrollLeft,
      scrollTop: el.scrollTop,
      moved: false,
    };
    el.classList.add("dragging");
  }, []);

  const handleMouseMove = useCallback((e) => {
    if (!drag.current.active) return;
    const el = scrollRef.current;
    const dx = e.pageX - drag.current.startX;
    const dy = e.pageY - drag.current.startY;
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
      drag.current.moved = true; // past this threshold, treat as a pan, not a click
    }
    el.scrollLeft = drag.current.scrollLeft - dx;
    el.scrollTop = drag.current.scrollTop - dy;
  }, []);

  const handleMouseUp = useCallback(() => {
    drag.current.active = false;
    scrollRef.current?.classList.remove("dragging");
  }, []);

  useEffect(() => {
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [handleMouseMove, handleMouseUp]);

  const toggle = useCallback((id) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  const { positioned, edges } = useMemo(
    () => layoutTree(data, expanded),
    [data, expanded]
  );

  const maxX = Math.max(...positioned.map((n) => n.x)) + NODE_WIDTH + PADDING;
  const maxY = Math.max(...positioned.map((n) => n.y)) + NODE_HEIGHT + PADDING;

  return (
    <div className="mindmap-viewport">
      <div
        className="mindmap-canvas-scroll"
        ref={scrollRef}
        onMouseDown={handleMouseDown}
      >
      <div className="mindmap-canvas" style={{ width: maxX, height: maxY }}>
        <svg className="mindmap-edges" width={maxX} height={maxY}>
          {edges.map((e, i) => (
            <path
              key={i}
              d={bezierPath(
                { x: e.from.x, y: e.from.y + NODE_HEIGHT / 2 },
                { x: e.to.x, y: e.to.y + NODE_HEIGHT / 2 }
              )}
              fill="none"
              stroke={e.color}
              strokeWidth={1.5}
            />
          ))}
        </svg>

        {positioned.map((n) => (
          <div
            key={n.id}
            className={`mindmap-node depth-${n.depth}`}
            style={{
              left: n.x,
              top: n.y,
              width: NODE_WIDTH,
              height: NODE_HEIGHT,
              background: n.color.bg,
              borderColor: n.color.border,
            }}
            title={n.summary || n.label}
            onClick={() => {
              if (drag.current.moved) return; // ignore click that was actually a pan drag
              setSelectedNode(n);
              if (n.hasChildren) {
                toggle(n.id);
              }
            }}
          >
            <div className="mindmap-node-content">
              <div className="mindmap-node-label">
                {n.label}
              </div>
            </div>

            {n.hasChildren && (
              <button
                className="mindmap-toggle"
                style={{ background: n.color.accent }}
                onClick={(e) => {
                  e.stopPropagation();
                  toggle(n.id);
                }}
                aria-label={n.isExpanded ? "Collapse" : "Expand"}
              >
                {n.isExpanded ? "\u2039" : "\u203A"}
              </button>
            )}
          </div>
        ))}
      </div>
      </div>

      <div className="mindmap-details">
        <h2>{selectedNode.label}</h2>
        <p style={{ whiteSpace: "pre-line" }}>
          {selectedNode.summary}
        </p>
      </div>
    </div>
  );
}