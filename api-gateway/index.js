const express = require("express");
const axios = require("axios");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

// These will become K8s Service DNS names:
// e.g. http://shortener-service.default.svc.cluster.local:8000
const SHORTENER_URL = process.env.SHORTENER_SERVICE_URL || "http://localhost:8000";
const ANALYTICS_URL = process.env.ANALYTICS_SERVICE_URL || "http://localhost:8001";

// Route: Create short URL
app.post("/shorten", async (req, res) => {
  try {
    const response = await axios.post(`${SHORTENER_URL}/shorten`, req.body);
    res.json(response.data);
  } catch (e) {
    res.status(e.response?.status || 500).json({ detail: e.message });
  }
});

// Route: Redirect short URL
app.get("/r/:code", async (req, res) => {
  try {
    const response = await axios.get(`${SHORTENER_URL}/resolve/${req.params.code}`);
    // Fire-and-forget: record the click in analytics service
    axios.post(`${ANALYTICS_URL}/click/${req.params.code}`).catch(() => {});
    res.redirect(response.data.url);
  } catch (e) {
    res.status(404).json({ detail: "Short URL not found" });
  }
});

// Route: Get analytics for a code
app.get("/analytics/:code", async (req, res) => {
  try {
    const response = await axios.get(`${ANALYTICS_URL}/analytics/${req.params.code}`);
    res.json(response.data);
  } catch (e) {
    res.status(e.response?.status || 500).json({ detail: e.message });
  }
});

// Health check endpoint — used for K8s liveness/readiness probes
app.get("/health", (req, res) => res.json({ status: "ok", service: "api-gateway" }));

app.listen(3000, () => console.log("API Gateway running on port 3000"));
