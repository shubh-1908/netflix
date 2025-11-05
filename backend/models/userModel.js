import db from "../db.js";
import bcrypt from "bcryptjs";

export const createUser = async (full_name, email, password) => {
  const hashed = await bcrypt.hash(password, 10);
  return new Promise((resolve, reject) => {
    db.query(
      "INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)",
      [full_name, email, hashed],
      (err, result) => {
        if (err) return reject(err);
        resolve({ id: result.insertId, full_name, email });
      }
    );
  });
};

export const findUserByEmail = (email) => {
  return new Promise((resolve, reject) => {
    db.query("SELECT * FROM users WHERE email = ?", [email], (err, result) => {
      if (err) return reject(err);
      resolve(result[0]);
    });
  });
};
