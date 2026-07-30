import React, { useEffect, useState, useCallback } from "react";
import MindMap from "./components/MindMap";

const API_BASE = "http://localhost:5000";

export default function App() {
  const [mindmaps, setMindmaps] = useState(null);   // list from /api/mindmaps
  const [listError, setListError] = useState(null);

  const [selected, setSelected] = useState(null);    // {class_name, subject, chapter}
  const [treeData, setTreeData] = useState(null);
  const [treeError, setTreeError] = useState(null);
  const [treeLoading, setTreeLoading] = useState(false);

  // Fetch the list of all saved mindmaps on page load
  useEffect(() => {
    fetch(`${API_BASE}/api/mindmaps`)
      .then((res) => {
        if (!res.ok) throw new Error(`Server responded ${res.status}`);
        return res.json();
      })
      .then((data) => setMindmaps(data.mindmaps || []))
      .catch((err) => setListError(err.message));
  }, []);

  // Called when a card is clicked
  const openMindmap = useCallback((item) => {
    setSelected(item);
    setTreeData(null);
    setTreeError(null);
    setTreeLoading(true);

    fetch(
      `${API_BASE}/api/mindmap/${encodeURIComponent(item.class_name)}/${encodeURIComponent(item.subject)}/${encodeURIComponent(item.chapter)}`
    )
      .then((res) => {
        if (!res.ok) throw new Error(`Server responded ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setTreeData(data);
        setTreeLoading(false);
      })
      .catch((err) => {
        setTreeError(err.message);
        setTreeLoading(false);
      });
  }, []);

  const backToList = useCallback(() => {
    setSelected(null);
    setTreeData(null);
    setTreeError(null);
  }, []);

  // ---------- DETAIL VIEW ----------
  if (selected) {
    return (
      <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
        <div
          style={{
            padding: "12px 20px",
            borderBottom: "1px solid #2a2a35",
            display: "flex",
            alignItems: "center",
            gap: 16,
            fontFamily: "sans-serif",
          }}
        >
          <button
            onClick={backToList}
            style={{
              background: "#2a2a35",
              color: "#e2e2ea",
              border: "none",
              borderRadius: 6,
              padding: "6px 14px",
              cursor: "pointer",
            }}
          >
            ← Back
          </button>
          <span style={{ color: "#9fa3b0" }}>
            {selected.class_name} / {selected.subject} / {selected.chapter}
          </span>
        </div>

        <div style={{ flex: 1, overflow: "hidden" }}>
          {treeLoading && (
            <div style={{ color: "#9fa3b0", padding: 24, fontFamily: "sans-serif" }}>
              Loading mind map...
            </div>
          )}

          {treeError && (
            <div style={{ color: "#f0b34c", padding: 24, fontFamily: "sans-serif" }}>
              Couldn't load the mind map: {treeError}
            </div>
          )}

          {treeData && <MindMap data={treeData} />}
        </div>
      </div>
    );
  }

  // ---------- LIST VIEW ----------
  if (listError) {
    return (
      <div style={{ color: "#f0b34c", padding: 24, fontFamily: "sans-serif" }}>
        Couldn't load mindmap list: {listError}
        <br />
        Make sure the Flask backend is running on {API_BASE}.
      </div>
    );
  }

  if (mindmaps === null) {
    return (
      <div style={{ color: "#9fa3b0", padding: 24, fontFamily: "sans-serif" }}>
        Loading available mind maps...
      </div>
    );
  }

  if (mindmaps.length === 0) {
    return (
      <div style={{ color: "#9fa3b0", padding: 24, fontFamily: "sans-serif" }}>
        No mind maps generated yet. Hit the backend's
        <code style={{ margin: "0 6px" }}>
          /api/mindmap/&lt;class_name&gt;/&lt;subject&gt;/&lt;chapter&gt;
        </code>
        endpoint once to generate one.
      </div>
    );
  }

  return (
    <div style={{ padding: 24, fontFamily: "sans-serif" }}>
      <h1 style={{ color: "#e2e2ea", marginBottom: 20 }}>Mind Maps</h1>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
          gap: 16,
        }}
      >
        {mindmaps.map((item, i) => (
          <div
            key={i}
            onClick={() => openMindmap(item)}
            style={{
              background: "#20202a",
              border: "1px solid #33333f",
              borderRadius: 10,
              padding: "16px 18px",
              cursor: "pointer",
              transition: "border-color 0.15s ease",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.borderColor = "#6fa8ff")}
            onMouseLeave={(e) => (e.currentTarget.style.borderColor = "#33333f")}
          >
            <div style={{ color: "#a8a4f0", fontSize: 12, marginBottom: 6 }}>
              {item.class_name} · {item.subject}
            </div>
            <div style={{ color: "#e2e2ea", fontSize: 16, fontWeight: 600 }}>
              {item.chapter.replace(/_/g, " ")}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}