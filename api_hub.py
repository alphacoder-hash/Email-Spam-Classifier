import http.server
import socketserver
import json
import pickle
import sys
import os
from urllib.parse import urlparse, parse_qs

# Ensure src is in path for preprocessing
sys.path.append(os.getcwd())
try:
    from src.preprocessing import transform_text
except ImportError:
    # Minimal fallback transformation if src is missing
    print("Warning: src.preprocessing not found. Using local fallback.")
    def transform_text(text): return text.lower()

# --- LOAD MODELS ---
print("🏹 Loading Trained Forensic Models...")
try:
    with open('models/vectorizer.pkl', 'rb') as f:
        tfidf = pickle.load(f)
    with open('models/model.pkl', 'rb') as f:
        model = pickle.load(f)
    print("✅ Logic Hub Online: vectorizer.pkl & model.pkl loaded.")
except Exception as e:
    print(f"❌ Critical Error loading models: {e}")
    tfidf, model = None, None

PORT = 8000

class ForensicHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # --- API ENDPOINT: /scan ---
        if parsed_path.path == '/scan':
            query = parse_qs(parsed_path.query)
            msg = query.get('msg', [''])[0]
            
            if not tfidf or not model:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Engine not initialized"}).encode())
                return

            # Real Model Inference
            try:
                transformed = transform_text(msg)
                vector = tfidf.transform([transformed])
                # predict_proba returns [ [ham_prob, spam_prob] ]
                proba = model.predict_proba(vector)[0]
                
                # Dynamic Forensic Details (Optimized)
                urgency_tokens = ['urgent', 'now', 'soon', 'immediately', 'alert']
                finance_tokens = ['cash', 'prize', 'money', 'bank', 'account']
                words = msg.lower().split()
                
                response = {
                    "score": float(proba[1] * 100),
                    "spam": bool(proba[1] >= 0.5),
                    "isUrgent": any(w in words for w in urgency_tokens),
                    "isFinance": any(w in words for w in finance_tokens),
                    "tokens": [w.upper() for w in words if w in urgency_tokens or w in finance_tokens]
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        # Default: Serve static files from current directory (index.html, models/, etc)
        return super().do_GET()

# --- START SERVER ---
print(f"⚡ SpamGuard Pro Intelligence Hub starting on http://localhost:{PORT}")
with socketserver.TCPServer(("", PORT), ForensicHandler) as httpd:
    httpd.serve_forever()
