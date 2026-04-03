from flask import Flask, request, jsonify, send_from_directory
import pickle
import os
import sys
from pathlib import Path

# Absolute Path Tracking
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

try:
    from src.preprocessing import transform_text
except ImportError:
    def transform_text(text): return text.lower()

app = Flask(__name__)

# --- LAZY LOAD MODELS ---
VECTORIZER_PATH = ROOT_DIR / 'models' / 'vectorizer.pkl'
MODEL_PATH = ROOT_DIR / 'models' / 'model.pkl'

tfidf = None
model = None

def load_models():
    global tfidf, model
    if tfidf is None:
        if not VECTORIZER_PATH.exists():
            raise FileNotFoundError(f"Forensic Asset Missing: {VECTORIZER_PATH}")
        with open(VECTORIZER_PATH, 'rb') as f:
            tfidf = pickle.load(f)
    if model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Forensic Asset Missing: {MODEL_PATH}")
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)

@app.route('/api/scan', methods=['GET'])
def scan():
    try:
        load_models()
        msg = request.args.get('msg', '')
        if not msg:
            return jsonify({"error": "No message provided"}), 400

        transformed = transform_text(msg)
        vector = tfidf.transform([transformed])
        proba = model.predict_proba(vector)[0]
        
        words = msg.lower().split()
        urgency_tokens = ['urgent', 'now', 'soon', 'immediately', 'alert', 'call']
        finance_tokens = ['cash', 'prize', 'money', 'bank', 'account']

        # --- Forensic Intelligence Nudge (Phishing Guard) ---
        delivery_scam_words = ['ups', 'fedex', 'dhl', 'package', 'delivery', 'address', 'shipping', 'track', 'issue']
        has_suspicious_link = any(x in msg.lower() for x in ['http', 'bit.ly', '.com', '.net', '.org', 'link', 'click', 'here', 'update'])
        is_delivery_scam = any(w in words for w in delivery_scam_words) and has_suspicious_link
        
        response = {
            "score": float(proba[1] * 100),
            "modelScore": float(proba[1] * 100),
            "spam": bool(proba[1] >= 0.5 or is_delivery_scam),
            "forensicAnomaly": bool(is_delivery_scam and proba[1] < 0.5),
            "engine": "MultinomialNB (model.pkl)",
            "isUrgent": any(w in words for w in urgency_tokens) or is_delivery_scam,
            "isFinance": any(w in words for w in finance_tokens),
            "tokens": [w.upper() for w in words if w in urgency_tokens or w in finance_tokens or w in delivery_scam_words]
        }
        return jsonify(response)
    except Exception as e:
        import traceback
        print(f"CRITICAL FORENSIC ERROR: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    try:
        # Instant serve of frontend without loading models
        return send_from_directory(str(ROOT_DIR), 'index.html')
    except Exception as e:
        return f"System Initialization Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(port=8080)
