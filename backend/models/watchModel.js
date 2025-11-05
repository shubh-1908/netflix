import db from "../db.js";

export const addWatchHistory = async (user_id, video_title, genre, duration) => {
  const query = `
    INSERT INTO watch_history (user_id, video_title, genre, duration, watched_at)
    VALUES (?, ?, ?, ?, NOW())
  `;
  await db.execute(query, [user_id, video_title, genre, duration]);
};

export const getWatchHistory = async () => {
  const [rows] = await db.execute(`SELECT * FROM watch_history`);
  return rows;
};
