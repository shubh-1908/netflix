import express from "express";
import fs from "fs";
import path from "path";
import { exec } from "child_process";
import db from "../db.js";

const router = express.Router();

// ✅ STEP 1: Generate churn data (DB → CSV → Python model)
router.get("/run-churn", async (req, res) => {
  try {
    const csvPath = path.resolve("ml/netflix_churn_data.csv");

    // ✅ Fresh query (fetch all users every time)
    const query = `
      SELECT 
        u.id AS user_id,
        u.full_name,
        u.email,
        IFNULL(COUNT(w.id), 0) AS num_videos_watched,
        IFNULL(AVG(w.duration_minutes), 0) AS avg_watch_time_per_day,
        IFNULL(MAX(DATEDIFF(NOW(), w.watched_at)), 0) AS last_login_days_ago,
        0 AS support_tickets,
        6 AS tenure_months,
        0 AS churn
      FROM users u
      LEFT JOIN watch_history w ON u.id = w.user_id
      GROUP BY u.id, u.full_name, u.email;
    `;

    // ✅ Always force a fresh DB fetch (no old connection cache)
    db.query(query, (err, results) => {
      if (err) {
        console.error("❌ DB Query Error:", err);
        return res.status(500).json({ success: false, message: "Database export failed" });
      }

      if (!results || results.length === 0) {
        console.log("⚠️ No user records found in DB");
        return res.status(404).json({ success: false, message: "No user data found" });
      }

      // ✅ Always rebuild the CSV file (overwrite old data)
      const header = Object.keys(results[0]).join(",") + "\n";
      const rows = results
        .map((r) =>
          Object.values(r)
            .map((v) => (v === null ? 0 : String(v).replace(/,/g, "")))
            .join(",")
        )
        .join("\n");

      // ✅ Write updated CSV safely (overwrite old file)
      fs.writeFileSync(csvPath, header + rows, "utf-8");
      console.log("📄 CSV regenerated with", results.length, "users from DB");

      // 🚀 Run churn prediction
      exec("python ./ml/churn_predict.py", { encoding: "utf8" }, (error, stdout, stderr) => {
        if (error) {
          console.error("❌ ML Execution Error:", stderr || error.message);
          return res.status(500).json({
            success: false,
            message: "ML model execution failed",
            error: stderr || error.message,
          });
        }

        console.log(stdout);
        res.json({
          success: true,
          message: "✅ Churn analysis updated successfully!",
          totalUsers: results.length,
        });
      });
    });
  } catch (err) {
    console.error("❌ Error generating churn data:", err);
    res.status(500).json({ success: false, message: "Internal server error" });
  }
});

// ✅ STEP 2: Send churn results to frontend
router.get("/churn-data", (req, res) => {
  const churnPath = path.resolve("ml/churn_results.csv");

  if (!fs.existsSync(churnPath)) {
    return res.status(404).json({
      success: false,
      message: "No churn results found — run /api/admin/run-churn first",
    });
  }

  try {
    const raw = fs.readFileSync(churnPath, "utf-8").trim();
    const [headerLine, ...rows] = raw.split("\n");
    const headers = headerLine.split(",");

    const data = rows.map((line) => {
      const values = line.split(",");
      const obj = {};
      headers.forEach((h, i) => (obj[h] = values[i]));
      return obj;
    });

    console.log(`✅ Sending ${data.length} churn records`);
    res.json({ success: true, data });
  } catch (err) {
    console.error("❌ Error reading churn results:", err);
    res.status(500).json({ success: false, message: "Failed to read churn results" });
  }
});

export default router;
