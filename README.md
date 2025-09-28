# ♻️ Plastic AI – Waste Classification & Eco Awareness  

This project is a **full-stack web application** that helps users classify waste items (e.g., plastic bottles, bags, cans), track eco-friendly stats, and learn sustainable disposal methods.  
It combines a **FastAPI (Python) backend** for AI classification with a **Node.js + Express backend** for authentication, user profiles, and serving the frontend.

---

## 🚀 Features
- 📸 **Image Upload & Classification** – Upload waste images and get classification with eco-tips.  
- 📊 **Dashboard** – Track your eco-score, streaks, carbon savings, and waste redirected.  
- 🔑 **User Authentication** – Register & login using JWT-based authentication.  
- 🌍 **Multi-Language Support** – Predictions can return localized disposal tips.  
- 🗂 **MongoDB Integration** – Store user accounts and eco stats.  
- 🎨 **Frontend Pages**  
  - `/` → Login  
  - `/register.html` → Register  
  - `/dashboard.html` → Eco Dashboard  
  - `/profile.html` → Profile  

---

## 🛠️ Tech Stack
- **Frontend**: HTML, CSS, JavaScript (served via Express)  
- **Backend (Node)**: Express.js, MongoDB, JWT Auth  
- **Backend (Python)**: FastAPI, TensorFlow/Keras (MobileNetV2), Uvicorn  
- **Database**: MongoDB (Atlas / Render)  
- **Deployment**: Render  

---


NITK2025/
│── server.js # Node.js backend (auth, profile, serving frontend)
│── model_server.py # FastAPI backend (image classification)
│── requirements.txt # Python dependencies
│── package.json # Node.js dependencies
│── index.html # Login page
│── register.html # Registration page
│── dashboard.html # Dashboard page
│── profile.html # Profile page
│── images/ # Static images (eco tips, icons, etc.)



---

## ⚡ Local Setup

### 1️⃣ Clone Repo
```bash
git clone https://github.com/Majenayu/NITK2025.git
cd NITK2025


python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

pip install -r requirements.txt
uvicorn model_server:app --reload --host 0.0.0.0 --port 8000


npm install
node server.js




## 📂 Project Structure



## 🧭 User Flow – How to Use the App

1. **Register / Login**
   - Go to 👉 [https://nitk2025-node.onrender.com](https://nitk2025-node.onrender.com)  
   - First, try to **Register** with your own email.  
   - ⚡ If registration/login fails, you can use this test account:  
     - **Email:** `vvce23cseaiml0100@vvce.ac.in`  
     - **Password:** `q`

2. **Dashboard Features**
   - 🌗 **Dark / Light Theme Toggle** – switch between light and dark mode.  
   - 🌍 **Language Switcher** – choose between **Kannada, English, Hindi**.  
   - 🔊 **Text-to-Speech** – click the speaker icon to listen to disposal tips and eco info in your selected language.  

3. **Upload an Image**
   - Prepare a sample image of **plastic cover, lithium battery, or aerosol**.  
   - You can download test images from this Google Drive folder 👉 [Sample Images](https://drive.google.com/drive/folders/1OmELpPXIl-ad3nYH5NaZSyLPs78Ly7pA?usp=sharing).  
   - On the **Dashboard**, click **Upload Image**, select your file, and submit.

4. **View AI Results**
   - The backend AI (FastAPI + TensorFlow) will classify your waste item.  
   - You’ll get:
     - ✅ **Disposal Tips** (how to dispose responsibly)  
     - ⚠️ **Environmental Impact** (effects of wrong disposal)  
     - 🌱 **Alternative Suggestions** (eco-friendly replacements)  
     - 🎨 **Creative Reuse Ideas** (repurpose ideas + YouTube links)  
   - Your **eco-stats** (ecoScore, carbon saved, waste redirected) are automatically updated.

---

💡 Tip: Explore all dashboard features (theme toggle, language switch, TTS) to get the best experience!

