const express = require("express");
const multer = require("multer");
const cors = require("cors");
const axios = require("axios");
const FormData = require("form-data");
const mongoose = require("mongoose");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");

const app = express();
app.use(cors());
app.use(express.json()); // to parse JSON body

// ====== MongoDB Connection ======
const MONGO_URI = "mongodb+srv://nitk:nitk@nitk.pnmruzy.mongodb.net/?retryWrites=true&w=majority&appName=nitk";
mongoose.connect(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log("✅ MongoDB connected"))
  .catch(err => console.error("❌ MongoDB error:", err));

// ====== User Schema ======
// ====== User Schema ======
const userSchema = new mongoose.Schema({
  name: String,
  email: { type: String, unique: true },
  password: String,
  stats: {
  totalClassifications: { type: Number, default: 0 },
  ecoScore: { type: Number, default: 0 },
  currentStreak: { type: Number, default: 0 },
  lastActiveDate: { type: String, default: null },
  carbonSaved: { type: Number, default: 0 },
  wasteRedirected: { type: Number, default: 0 },
  energySaved: { type: Number, default: 0 }
}

});
const User = mongoose.model("User", userSchema);

// Example impact values (same as profile.html mapping)
const carbonImpactValues = {
  "plastic bottle": { co2Saved: 0.5, energySaved: 2.5 },
  "plastic bag": { co2Saved: 0.2, energySaved: 1.0 },
  "plastic cover": { co2Saved: 0.15, energySaved: 0.8 },
  "plastic": { co2Saved: 0.3, energySaved: 1.5 },
  "other": { co2Saved: 0.1, energySaved: 0.5 }
};


// ====== Auth Routes ======

// Register
app.post("/register", async (req, res) => {
  try {
    const { name, email, password } = req.body;
    const existingUser = await User.findOne({ email });
    if (existingUser) return res.status(400).json({ error: "User already exists" });

    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = new User({ name, email, password: hashedPassword });
    await newUser.save();

    res.json({ message: "User registered successfully" });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Login
app.post("/login", async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ email });
    if (!user) return res.status(400).json({ error: "User not found" });

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) return res.status(400).json({ error: "Invalid credentials" });

    // JWT token (can be used later for auth middleware)
    const token = jwt.sign({ id: user._id }, "secret_key", { expiresIn: "1h" });
    res.json({ message: "Login successful", token });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const storage = multer.memoryStorage();
const upload = multer({ storage });

app.post("/upload", authMiddleware, upload.single("image"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: "No file uploaded" });
    }

    const lang = req.query.lang || "en";

    const formData = new FormData();
    formData.append("file", req.file.buffer, {
      filename: req.file.originalname,
      contentType: req.file.mimetype,
    });

    // Call Python API
    const response = await axios.post(
      `http://localhost:8000/predict?language=${lang}`,
      formData,
      { headers: formData.getHeaders() }
    );

    const result = response.data;

    // === Update user stats in DB ===
    const user = await User.findById(req.userId);
    if (user) {
      const today = new Date().toDateString();

      // Update streak
      if (user.stats.lastActiveDate === today) {
        // already counted today
      } else if (user.stats.lastActiveDate === new Date(Date.now() - 86400000).toDateString()) {
        user.stats.currentStreak += 1;
      } else {
        user.stats.currentStreak = 1;
      }

      // Example impact values (same as profile.html mapping)
const carbonImpactValues = {
  "plastic bottle": { co2Saved: 0.5, energySaved: 2.5 },
  "plastic bag": { co2Saved: 0.2, energySaved: 1.0 },
  "plastic cover": { co2Saved: 0.15, energySaved: 0.8 },
  "plastic": { co2Saved: 0.3, energySaved: 1.5 },
  "other": { co2Saved: 0.1, energySaved: 0.5 }
};


const impact = carbonImpactValues[result.wasteType.toLowerCase()] || { co2Saved: 0.1, energySaved: 0.5 };

user.stats.totalClassifications += 1;
user.stats.ecoScore += 10;
user.stats.carbonSaved += impact.co2Saved;
user.stats.energySaved += impact.energySaved;
user.stats.wasteRedirected += 1;
await user.save();

    }

    res.json({
      imageUrl: `data:${req.file.mimetype};base64,${req.file.buffer.toString("base64")}`,
      ...result,
    });

  } catch (err) {
    console.error("❌ Error:", err.message);
    res.status(500).json({ error: "Failed to classify image" });
  }
});


// Middleware to verify JWT
function authMiddleware(req, res, next) {
  const authHeader = req.headers["authorization"];
  if (!authHeader) return res.status(401).json({ error: "No token provided" });

  const token = authHeader.split(" ")[1];
  if (!token) return res.status(401).json({ error: "Invalid token format" });

  try {
    const decoded = jwt.verify(token, "secret_key");
    req.userId = decoded.id;
    next();
  } catch (err) {
    return res.status(401).json({ error: "Invalid or expired token" });
  }
}

// Profile route
app.get("/profile", authMiddleware, async (req, res) => {
  try {
    const user = await User.findById(req.userId).select("-password");
    if (!user) return res.status(404).json({ error: "User not found" });

    res.json({
      name: user.name,
      email: user.email,
      stats: user.stats
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});





app.listen(5000, () => {
  console.log("🚀 Node server running on http://localhost:5000");
});
