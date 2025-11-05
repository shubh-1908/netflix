// backend/routes/watchRoutes.js
import express from "express";
import db from "../db.js";
import { exec } from "child_process";

const router = express.Router();

// ✅ Add a new watch event
router.post("/add", (req, res) => {
  const { user_id, video_title, genre, duration_minutes } = req.body;

  if (!user_id || !video_title) {
    return res.status(400).json({ message: "Missing watch info" });
  }

  const query = `
    INSERT INTO watch_history (user_id, video_title, genre, duration_minutes, watched_at)
    VALUES (?, ?, ?, ?, NOW())
  `;

  db.query(query, [user_id, video_title, genre, duration_minutes], (err) => {
    if (err) {
      console.error("❌ Watch insert error:", err);
      return res.status(500).json({ message: "Database error" });
    }

    console.log(`🎬 Watch added for user_id=${user_id}`);

    // ✅ Trigger churn model retraining automatically
    exec("python ./ml/churn_predict.py", (error, stdout, stderr) => {
      if (error) {
        console.error("⚠️ ML model failed:", error);
      } else {
        console.log("✅ Churn model auto-updated after watch event");
      }
    });

    res.json({ success: true, message: "Watch logged successfully" });
  });
});

export default router;
