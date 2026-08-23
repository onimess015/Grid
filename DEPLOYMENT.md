# 🚀 Streamlit Cloud Deployment Guide for GridSelect

This repository is pre-configured for **instant 1-click deployment** on **[Streamlit Community Cloud](https://share.streamlit.io)**.

---

## 📋 Deployment Settings on Streamlit Cloud

When deploying on [Streamlit Cloud](https://share.streamlit.io), use these exact settings:

| Setting | Value |
| :--- | :--- |
| **Repository** | `onimess015/Grid` |
| **Branch** | `main` |
| **Main file path** | `app.py` |
| **App URL** | *Custom or auto-generated* |

---

## ⚙️ Included Deployment Files

1. **`app.py`**: Entry point for the multi-page application.
2. **`requirements.txt`**: Minimal, pinned dependencies (`streamlit`, `pandas`, `numpy`, `plotly`).
3. **`.streamlit/config.toml`**: Custom industrial theme colors (Navy `#0B2545`, White `#FFFFFF`, Background `#F5F7FA`) and server settings.
4. **`data/`**: Demo CSV files bundled within the repository so no external database is needed.
5. **`pages/`**: Native Streamlit multipage application structure.

---

## 🛠️ Step-by-Step Deployment Instructions

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "feat: complete GridSelect Power Systems platform"
   git push -u origin main
   ```

2. **Deploy on Streamlit Community Cloud:**
   - Go to **[share.streamlit.io](https://share.streamlit.io)**.
   - Click **"Create app"** (or **"New app"**).
   - Select your repository: `onimess015/Grid`.
   - Set **Main file path** to `app.py`.
   - Click **"Deploy!"**.

3. **Your application will be live in 1-2 minutes!**
