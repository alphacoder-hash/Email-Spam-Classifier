from flask import Flask, request, jsonify
import pickle
import os
import re
import string
from pathlib import Path

# Absolute Path Tracking
ROOT_DIR = Path(__file__).parent.parent.absolute()

# --- ZERO-FAULT FORENSIC PREPROCESSING ---
def transform_text(text):
    # Standardize & Normalize
    text = text.lower()
    
    # Regex-based high-precision tokenization (No NLTK needed)
    tokens = re.findall(r'[a-z0-9]+', text)

    # Professional Stopword Mitigation (Self-healing list)
    stop_words = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', 'to', "won't", 'wouldn', "wouldn't"}

    y = []
    for i in tokens:
        if i not in stop_words and i not in string.punctuation:
            y.append(i)

    # High-speed return (cloud optimized)
    # Stemming is omitted for maximum cloud speed unless strictly required
    return " ".join(y)

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

if __name__ == '__main__':
    app.run(port=8080)
