from flask import Flask, request, jsonify
import pickle
import os
import sys

# Support relative paths for Vercel
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from src.preprocessing import transform_text
except ImportError:
    # Minimal fallback transformation if src is missing
    def transform_text(text): return text.lower()

app = Flask(__name__)

# --- LOAD MODELS ---
# Path resolution for Vercel functions (models/ is in the root)
VECTORIZER_PATH = os.path.join(parent_dir, 'models', 'vectorizer.pkl')
MODEL_PATH = os.path.join(parent_dir, 'models', 'model.pkl')

tfidf = None
model = None

def load_models():
    global tfidf, model
    if tfidf is None:
        with open(VECTORIZER_PATH, 'rb') as f:
            tfidf = pickle.load(f)
    if model is None:
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
        
        # Determine Forensic Confidence (Nudge)
        final_score = float(proba[1] * 100)
        forensic_anomaly = False
        
        if is_delivery_scam:
            forensic_anomaly = True
            # We flag it as an anomaly if it's potentially a zero-day delivery scam
        
        response = {
            "score": final_score,
            "modelScore": float(proba[1] * 100),
            "spam": bool(proba[1] >= 0.5 or forensic_anomaly),
            "forensicAnomaly": forensic_anomaly,
            "engine": "MultinomialNB (model.pkl)",
            "isUrgent": any(w in words for w in urgency_tokens) or is_delivery_scam,
            "isFinance": any(w in words for w in finance_tokens),
            "tokens": [w.upper() for w in words if w in urgency_tokens or w in finance_tokens or w in delivery_scam_words]
        }
        return jsonify(response)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return send_from_directory(parent_dir, 'index.html')

if __name__ == '__main__':
    from flask import send_from_directory
    app.run(port=8080)
