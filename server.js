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

// ====== Environment Variables ======
const MONGO_URI = process.env.MONGO_URI; // set in Render dashboard
const JWT_SECRET = process.env.JWT_SECRET || "fallback_secret";
const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";

// ====== MongoDB Connection ======
mongoose.connect(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log("✅ MongoDB connected"))
  .catch(err => console.error("❌ MongoDB error:", err));

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

// ====== Auth Routes ======
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

app.post("/login", async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ email });
    if (!user) return res.status(400).json({ error: "User not found" });

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) return res.status(400).json({ error: "Invalid credentials" });

    const token = jwt.sign({ id: user._id }, JWT_SECRET, { expiresIn: "1h" });
    res.json({ message: "Login successful", token });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Middleware to verify JWT
function authMiddleware(req, res, next) {
  const authHeader = req.headers["authorization"];
  if (!authHeader) return res.status(401).json({ error: "No token provided" });

  const token = authHeader.split(" ")[1];
  if (!token) return res.status(401).json({ error: "Invalid token format" });

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.userId = decoded.id;
    next();
  } catch (err) {
    return res.status(401).json({ error: "Unauthorized" });
  }
}

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

    // Call Python API (Render URL from env var)
    const response = await axios.post(
      `${PYTHON_API_URL}/predict?language=${lang}`,
      formData,
      { headers: formData.getHeaders() }
    );

    const result = response.data;

    // === Update user stats in DB ===
    const user = await User.findById(req.userId);
    if (user) {
      const today = new Date().toDateString();

      if (user.stats.lastActiveDate === today) {
        // already counted today
      } else if (user.stats.lastActiveDate === new Date(Date.now() - 86400000).toDateString()) {
        user.stats.currentStreak += 1;
      } else {
        user.stats.currentStreak = 1;
      }

      user.stats.lastActiveDate = today;
      user.stats.totalClassifications += 1;
      user.stats.ecoScore += 10;
      user.stats.carbonSaved += 0.3;
      user.stats.energySaved += 1.2;
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

// Profile endpoint
app.get("/profile", authMiddleware, async (req, res) => {
  try {
    const user = await User.findById(req.userId);
    if (!user) return res.status(404).json({ error: "User not found" });

    res.json({ name: user.name, email: user.email, stats: user.stats });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const path = require("path");

// ... keep everything you already have ...

// === Serve frontend (index page) ===
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "index.html"));

});
app.get("/profile", (req, res) => {
  res.sendFile(path.join(__dirname, "profile.html"));
});

app.get("/register", (req, res) => {
  res.sendFile(path.join(__dirname, "register.html"));
});

app.get("/dashboard", (req, res) => {
  res.sendFile(path.join(__dirname, "dashboard.html"));
});


// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Node server running on port ${PORT}`));
