import { useState } from "react";
import axios from "axios";

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const generateMindmap = async () => {
    setLoading(true);
    setResult(null);

    try {
      const res = await axios.post("http://127.0.0.1:5000/generate", {
        class_name: "class10",
        subject: "science",
        chapter: "life_processes",
      });

      setResult(res.data);
    } catch (err) {
      console.log("Error:", err);
    }

    setLoading(false);
  };

  return (
    <div className="container">
      <h1>🧠 Mind Map AI</h1>

      <button onClick={generateMindmap} className="btn">
        Generate Mind Map
      </button>

      {loading && <p className="loading">Generating mind map... ⏳</p>}

      {result && (
        <div className="output">
          <h2>Output</h2>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;