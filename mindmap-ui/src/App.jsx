import React, { useEffect, useState } from "react";
import MindMap from "./components/MindMap";

const API_BASE = "http://localhost:5000";

export default function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/mindmap/life_processes`)
      .then((res) => {
        if (!res.ok) throw new Error(`Server responded ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return (
      <div style={{ color: "#f0b34c", padding: 24, fontFamily: "sans-serif" }}>
        Couldn't load the mind map: {error}
        <br />
        Make sure the Flask backend is running on {API_BASE}.
      </div>
    );
  }

  if (!data) {
    return (
      <div style={{ color: "#9fa3b0", padding: 24, fontFamily: "sans-serif" }}>
        Generating mind map... (this can take a moment on first load)
      </div>
    );
  }

  return <MindMap data={data} />;
}