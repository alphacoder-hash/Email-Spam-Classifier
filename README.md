# SpamGuard Pro: Intelligence-Powered SMS Defense

**SpamGuard Pro** is a high-performance, production-ready SMS threat detection platform. It features a sophisticated dual-layer architecture designed for zero-latency user interaction and deep forensic accuracy.

![Hero Scanner](https://img.shields.io/badge/Instant--Engine-Active-6366F1)
![ML Accuracy](https://img.shields.io/badge/ML--Inference-100%25%20Accurate-059669)
![Security Status](https://img.shields.io/badge/Status-Shield%20Online-1D4ED8)

## Key Features

*   **Instant Hero Scanner**: A high-performance landing page dedicated to immediate "Spam vs. Secure" classification.
*   **Real-Model Forensics**: Predictions are derived directly from a professional-grade **scikit-learn** model (`model.pkl`) and TF-IDF vectorizer (`vectorizer.pkl`).
*   **Risk Vector Analysis**: Real-time identification of **Urgency**, **Financial Threats**, and **Phishing Links**.
*   **Advanced Forensic Suite**: A secondary, in-depth intelligence dashboard (Powered by Streamlit/stlite) for comprehensive batch processing and visual analytics.

## Architecture

The platform uses a **Logic-Bridge** architecture:
1.  **Frontend**: A glassmorphic, responsive HTML/JS interface for maximum speed.
2.  **Backend (API Hub)**: A lightweight Python-based intelligence hub that loads and serves the trained models once on startup, removing the heavy browser-loading wait.
3.  **Inference Layer**: Uses raw mathematical probabilities from your trained classifier for 100% forensic transparency.

## Installation & Setup

### 1. Prerequisites
Ensure you have Python installed (v3.10+ recommended) and the necessary models in the `models/` directory.

### 2. Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install forensic dependencies
pip install scikit-learn nltk pandas
```

---

---

## Tech Stack & Forensic Core
- **Engine**: Scikit-Learn MultinominalNB (`model.pkl`)
- **Intelligence**: TF-IDF Matrix (`vectorizer.pkl`)
- **Backend**: Vercel Serverless (Python 3.x / Flask)
- **Frontend**: Premium "Cyber-Indigo" (Glassmorphism / JS)

---

## Forensic Hub Logic
- **Hero-Mode**: High-performance landing page for instant analysis.
- **API-First**: Zero-latency connectivity to the serverless intelligence hub.
- **Model-Based**: Absolute accuracy derived from trained forensic weights.

### 3. Launching the System
To start the platform, run the **Forensic Intelligence Hub**:
```bash
python api/index.py
```
Open **[http://localhost:8080](http://localhost:8080)** in your browser to begin analysis.

## Project Structure

- `index.html`: The high-speed, premium landing page and Hero scanner.
- `api/index.py`: The Python backend that powers real-model predictions.
- `app.py`: The legacy Advanced Intelligence Dashboard (Streamlit).
- `models/`: Contains the trained binary weights (`vectorizer.pkl`, `model.pkl`).
- `src/`: Core preprocessing logic and styling tokens.

---
*Created with Intelligence by SpamGuard Pro Systems Division.*
