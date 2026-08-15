import React, { useEffect, useState, useCallback, useMemo } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Sidebar from "./components/Sidebar";
import MindMapFlow from "./components/MindMapFlow";
import LearningPanel from "./components/LearningPanel";
import { convertTreeToReactFlow } from "./utils/treeToReactFlow";
import { Sparkles, Layers, BookOpen, RefreshCw, Compass } from "lucide-react";

const API_BASE = "http://localhost:5000";

export default function App() {
  const [mindmaps, setMindmaps] = useState(null);
  const [listError, setListError] = useState(null);

  const [selectedMindmap, setSelectedMindmap] = useState(null);
  const [treeData, setTreeData] = useState(null);
  const [treeError, setTreeError] = useState(null);
  const [treeLoading, setTreeLoading] = useState(false);

  const [uploadFile, setUploadFile] = useState(null);
  const [uploadClass, setUploadClass] = useState("");
  const [uploadSubject, setUploadSubject] = useState("");
  const [uploadChapter, setUploadChapter] = useState("");
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");

  const [expandedNodeIds, setExpandedNodeIds] = useState(() => new Set());
  const [selectedNodeId, setSelectedNodeId] = useState(null);

  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isLearningPanelOpen, setIsLearningPanelOpen] = useState(false);

  // Fetch list of all mindmaps on initial load
  useEffect(() => {
    fetch(`${API_BASE}/api/mindmaps`)
      .then((res) => {
        if (!res.ok) throw new Error(`Server responded with ${res.status}`);
        return res.json();
      })
      .then((data) => {
        const list = data.mindmaps || [];
        setMindmaps(list);
        if (list.length > 0) {
          openMindmap(list[0]);
        }
      })
      .catch((err) => setListError(err.message));
  }, []);

  // Helper to open a selected mindmap item
  const openMindmap = useCallback((item) => {
    setSelectedMindmap(item);
    setTreeData(null);
    setTreeError(null);
    setTreeLoading(true);
    setSelectedNodeId(null);
    setIsLearningPanelOpen(false);

    fetch(
      `${API_BASE}/api/mindmap/${item.class_name}/${item.subject}/${item.chapter}`
    )
      .then((res) => {
        if (!res.ok) throw new Error(`Server responded ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setTreeData(data);
        setTreeLoading(false);

        // Auto-expand root chapter node and first-level theme nodes
        const defaultExpanded = new Set();
        if (data.id) defaultExpanded.add(data.id);
        (data.children || []).forEach((c) => defaultExpanded.add(c.id));
        setExpandedNodeIds(defaultExpanded);

        // Select root chapter node by default
        if (data.id) {
          setSelectedNodeId(data.id);
        }
      })
      .catch((err) => {
        setTreeError(err.message);
        setTreeLoading(false);
      });
  }, []);

  const handleUpload = async () => {
  if (!uploadFile || !uploadClass || !uploadSubject || !uploadChapter) {
    setUploadMessage("Please fill all the fields.");
    return;
  }

  setUploadLoading(true);
  setUploadMessage("");

  const formData = new FormData();
  formData.append("file", uploadFile);
  formData.append("class_name", uploadClass);
  formData.append("subject", uploadSubject);
  formData.append("chapter_name", uploadChapter);

  try {
    const uploadResponse = await fetch(`${API_BASE}/api/upload`, {
      method: "POST",
      body: formData,
    });

    const uploadData = await uploadResponse.json();

    if (!uploadResponse.ok) {
      throw new Error(uploadData.error || "Upload failed");
    }

    setUploadMessage("PDF uploaded successfully. Generating mind map...");

    const mapResponse = await fetch(
      `${API_BASE}/api/mindmap/${uploadClass}/${uploadSubject}/${uploadChapter}`
    );

    const mapData = await mapResponse.json();

    if (!mapResponse.ok) {
      throw new Error(mapData.error || "Mind map generation failed");
    }

    setTreeData(mapData);
    setSelected({
      class_name: uploadClass,
      subject: uploadSubject,
      chapter: uploadChapter,
    });

    setUploadMessage("");
  } catch (error) {
    setUploadMessage(error.message);
  } finally {
    setUploadLoading(false);
  }
};

  // Handle node expand/collapse toggle
  const handleToggleExpand = useCallback((nodeId) => {
    setExpandedNodeIds((prev) => {
      const next = new Set(prev);
      if (next.has(nodeId)) {
        next.delete(nodeId);
      } else {
        next.add(nodeId);
      }
      return next;
    });
  }, []);

  // Handle node selection
  const handleSelectNode = useCallback((nodeId) => {
    setSelectedNodeId(nodeId);
    setIsLearningPanelOpen(true);
  }, []);

  // Find currently selected node object in treeData
  const activeNodeObject = useMemo(() => {
    if (!treeData || !selectedNodeId) return null;

    let found = null;
    function search(node) {
      if (node.id === selectedNodeId) {
        found = node;
        return;
      }
      for (const child of node.children || []) {
        search(child);
        if (found) return;
      }
    }
    search(treeData);
    return found;
  }, [treeData, selectedNodeId]);

  // Convert treeData to React Flow nodes and edges
  const { nodes, edges } = useMemo(() => {
    return convertTreeToReactFlow(treeData, expandedNodeIds, selectedNodeId);
  }, [treeData, expandedNodeIds, selectedNodeId]);

  return (
    <div className="flex h-screen w-screen bg-slate-950 overflow-hidden text-slate-100 font-sans select-none">
      {/* 1. LEFT PANEL: COLLAPSIBLE SIDEBAR */}
      <Sidebar
        mindmaps={mindmaps}
        selectedMindmap={selectedMindmap}
        onSelectMindmap={openMindmap}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      {/* 2. CENTER PANEL: MAIN MIND MAP CANVAS & TOP BREADCRUMB */}
      <main className="flex-1 relative flex flex-col h-full overflow-hidden bg-slate-950">
        {/* Top Floating Glassmorphic Header */}
        <header className="absolute top-4 left-4 right-4 z-10 flex items-center justify-between p-3 rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-slate-800/80 shadow-2xl">
          {/* Breadcrumb Navigation */}
          <div className="flex items-center gap-2 text-xs font-medium text-slate-400">
            <span className="flex items-center gap-1 text-slate-300">
              <Compass className="w-3.5 h-3.5 text-sky-400" />
              <span>{selectedMindmap?.class_name || "Class 10"}</span>
            </span>
            <span>/</span>
            <span className="text-slate-300">{selectedMindmap?.subject || "Science"}</span>
            <span>/</span>
            <span className="text-sky-400 font-semibold">
              {selectedMindmap?.chapter?.replace(/_/g, " ") || "Mind Map Explorer"}
            </span>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => selectedMindmap && openMindmap(selectedMindmap)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800/80 border border-slate-700/80 text-xs font-medium text-slate-300 hover:text-sky-400 hover:border-slate-600 transition-all"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Refresh Map</span>
            </button>
          </div>
        </header>

        {/* React Flow Canvas / Loading State / Error State */}
        <div className="flex-1 w-full h-full relative">
          {treeLoading && (
            <div className="absolute inset-0 z-20 flex flex-col items-center justify-center gap-3 bg-slate-950/80 backdrop-blur-md">
              <div className="p-3 rounded-2xl bg-sky-500/10 border border-sky-500/20 text-sky-400 animate-bounce">
                <Sparkles className="w-8 h-8" />
              </div>
              <span className="text-sm font-semibold text-slate-300">
                Loading Interactive Mind Map...
              </span>
            </div>
          )}

          {treeError && (
            <div className="absolute inset-0 z-20 flex flex-col items-center justify-center p-6 text-center bg-slate-950/90">
              <div className="p-3 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 mb-3">
                <BookOpen className="w-8 h-8" />
              </div>
              <h3 className="text-base font-bold text-slate-100 mb-1">Couldn't Load Mind Map</h3>
              <p className="text-xs text-amber-400 max-w-sm mb-4">{treeError}</p>
              <button
                onClick={() => selectedMindmap && openMindmap(selectedMindmap)}
                className="px-4 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 text-white text-xs font-semibold shadow-lg shadow-sky-500/20 transition-all"
              >
                Try Again
              </button>
            </div>
          )}

          {treeData && (
            <MindMapFlow
              initialNodes={nodes}
              initialEdges={edges}
              selectedNodeId={selectedNodeId}
              onSelectNode={handleSelectNode}
              onToggleExpand={handleToggleExpand}
            />
          )}
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

    <div
      style={{
        background: "#20202a",
        border: "1px solid #33333f",
        borderRadius: 10,
        padding: 20,
        marginBottom: 28,
      }}
    >
      <h2 style={{ color: "#e2e2ea", marginTop: 0 }}>
        Upload New Chapter
      </h2>

      <input
        type="file"
        accept=".pdf"
        onChange={(e) => setUploadFile(e.target.files[0])}
        style={{ marginBottom: 12, color: "#e2e2ea" }}
      />

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
        <input
          type="text"
          placeholder="Class (e.g. class10)"
          value={uploadClass}
          onChange={(e) => setUploadClass(e.target.value)}
        />

        <input
          type="text"
          placeholder="Subject (e.g. maths)"
          value={uploadSubject}
          onChange={(e) => setUploadSubject(e.target.value)}
        />

        <input
          type="text"
          placeholder="Chapter name"
          value={uploadChapter}
          onChange={(e) => setUploadChapter(e.target.value)}
        />

        <button
          onClick={handleUpload}
          disabled={uploadLoading}
          style={{
            background: "#6fa8ff",
            color: "#111",
            border: "none",
            borderRadius: 6,
            padding: "8px 16px",
            cursor: uploadLoading ? "not-allowed" : "pointer",
            fontWeight: 600,
          }}
        >
          {uploadLoading ? "Generating..." : "Upload & Generate"}
        </button>
      </div>

      {uploadMessage && (
        <div
          style={{
            marginTop: 12,
            color: "#f0b34c",
          }}
        >
          {uploadMessage}
        </div>
      )}
    </div>

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