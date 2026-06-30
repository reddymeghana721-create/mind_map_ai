import { useState } from "react";
import axios from "axios";
import ReactFlow from "reactflow";
import "reactflow/dist/style.css";

function App() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [loading, setLoading] = useState(false);

  const generateMindmap = async () => {
    setLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:5000/generate", {
        class_name: "class10",
        subject: "science",
        chapter: "life_processes",
      });

      const data = res.data;

      // Convert backend format → ReactFlow format
      const formattedNodes = data.nodes.map((n, i) => ({
        id: n.id,
        data: { label: n.id },
        position: { x: i * 200, y: i * 100 },
      }));

      const formattedEdges = data.edges.map((e, i) => ({
        id: `e${i}`,
        source: e.from,
        target: e.to,
      }));

      setNodes(formattedNodes);
      setEdges(formattedEdges);
    } catch (err) {
      console.log(err);
    }

    setLoading(false);
  };

  return (
    <div style={{ height: "100vh", fontFamily: "Arial" }}>
      <h2 style={{ padding: "10px" }}>🧠 Mind Map AI</h2>

      <button
        onClick={generateMindmap}
        style={{ marginLeft: "10px", padding: "8px 15px" }}
      >
        Generate Mind Map
      </button>

      {loading && <p style={{ marginLeft: "10px" }}>Generating...</p>}

      <div style={{ height: "90vh" }}>
        <ReactFlow nodes={nodes} edges={edges} fitView />
      </div>
    </div>
  );
}

export default App;