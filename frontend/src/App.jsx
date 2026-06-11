import { useState } from "react";

function App() {
  const [longUrl, setLongUrl] = useState("");
  const [result, setResult] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState("");

  const API = "http://localhost:3000"; // API Gateway

  const shorten = async () => {
    setError("");
    setResult(null);
    try {
      const res = await fetch(`${API}/shorten`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: longUrl }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed");
      setResult(data);
    } catch (e) {
      setError(e.message);
    }
  };

  const getAnalytics = async (code) => {
    try {
      const res = await fetch(`${API}/analytics/${code}`);
      const data = await res.json();
      setAnalytics(data);
    } catch (e) {
      setError("Analytics fetch failed");
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "60px auto", fontFamily: "sans-serif" }}>
      <h1>🔗 URL Shortener</h1>

      <div style={{ display: "flex", gap: 8 }}>
        <input
          style={{ flex: 1, padding: 8, fontSize: 16 }}
          placeholder="Enter long URL..."
          value={longUrl}
          onChange={(e) => setLongUrl(e.target.value)}
        />
        <button onClick={shorten} style={{ padding: "8px 16px" }}>Shorten</button>
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <div style={{ marginTop: 24, padding: 16, border: "1px solid #ccc", borderRadius: 8 }}>
          <p><strong>Short URL:</strong>{" "}
            <a href={`${API}/r/${result.code}`} target="_blank">{`${API}/r/${result.code}`}</a>
          </p>
          <p><strong>Code:</strong> {result.code}</p>
          <button onClick={() => getAnalytics(result.code)}>View Analytics</button>
        </div>
      )}

      {analytics && (
        <div style={{ marginTop: 16, padding: 16, background: "#f5f5f5", borderRadius: 8 }}>
          <h3>Analytics for /{analytics.code}</h3>
          <p>Total Clicks: <strong>{analytics.click_count}</strong></p>
          <p>Created At: {new Date(analytics.created_at).toLocaleString()}</p>
          <p>Last Accessed: {analytics.last_accessed
            ? new Date(analytics.last_accessed).toLocaleString()
            : "Never"}</p>
        </div>
      )}
    </div>
  );
}

export default App;
