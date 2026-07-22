# AI-Powered Radiology Report Audit & Quality Analyzer

A production-ready AI-powered quality assurance web application for radiology reports — built with HTML5/CSS3/JavaScript SPA and Python (Flask). Supports both **Groq (Llama 3.3 70B)** and **Google Gemini AI**.

> ⚠️ **Disclaimer:** This tool is for quality assurance and educational purposes only. It does not generate diagnoses or clinical advice. All suggestions must be reviewed by a qualified radiologist.

---

## 📁 Project Structure

```
index.html                      # Main Web Application entry point (GitHub Pages ready)
css/
  styles.css                    # Custom healthcare UI design system
js/
  app.js                        # SPA navigation & Groq / Gemini AI integration
sample_reports/                 # Demo radiology report text files
server.py                       # Flask backend (optional REST API server)
utils/                          # Backend utilities (text extraction, PDF generation)
requirements.txt
Procfile
runtime.txt
README.md
```

---

## 🚀 How to Deploy on GitHub Pages (Instant 1-Click)

1. Open your repository on GitHub.
2. Drag and drop all contents of this folder into your repository.
3. Click **Commit changes**.
4. Go to **Settings → Pages** → Select `main` branch and `/ (root)` folder → Click **Save**.
5. Your live app is instantly online at `https://your-username.github.io/repository-name/`!

---

## ☁️ How to Deploy on Render / Vercel (Flask Backend)

1. Connect your GitHub repository to [Render.com](https://render.com).
2. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn server:app`
3. Click **Create Web Service**.
