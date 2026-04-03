import streamlit as st
import pickle
import os
import sys
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io

# 1. Setup Page Config
st.set_page_config(page_title="SpamGuard Pro", page_icon="🛡️", layout="wide")

# 2. Add src to sys.path and load preprocessing
sys.path.append(os.path.join(os.getcwd(), 'src'))
try:
    from preprocessing import transform_text
except ImportError:
    # Fallback for direct runs if src not in path
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem.porter import PorterStemmer
    import string
    ps = PorterStemmer()
    def transform_text(text):
        text = text.lower()
        text = nltk.word_tokenize(text)
        y = [i for i in text if i.isalnum()]
        text = [i for i in y if i not in stopwords.words('english') and i not in string.punctuation]
        return " ".join([ps.stem(i) for i in text])

# Load CSS
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css(os.path.join('src', 'style.css'))

# 3. Load Assets
@st.cache_resource
def load_assets():
    tfidf = pickle.load(open(os.path.join('models', 'vectorizer.pkl'), 'rb'))
    model = pickle.load(open(os.path.join('models', 'model.pkl'), 'rb'))
    try:
        df = pd.read_csv(os.path.join('data', 'spam.csv'), encoding='latin-1')
        df = df.rename(columns={'v1': 'target', 'v2': 'text'})[['target', 'text']]
    except:
        df = pd.DataFrame({'target': ['ham'], 'text': ['Hello']})
    return tfidf, model, df

tfidf, model, dataset = load_assets()

# 4. Sidebar - Control Center
with st.sidebar:
    st.markdown("<h2 style='color: #6366F1; font-family: Outfit;'>SpamGuard Pro</h2>", unsafe_allow_html=True)
    st.divider()
    st.subheader("⚙️ Protection Settings")
    threshold = st.slider("Sensitivity Threshold", 0.0, 1.0, 0.5, 0.05, 
                         help="Adjust how 'strict' the model is. Higher threshold = fewer false positives.")
    
    st.divider()
    st.info("💡 **Pro Tip**: Use the 'Batch' tab for enterprise communication audits.")
    
# 5. Main Content - Tabs
st.markdown("### 🛡️ Intelligent Analysis Suite")
tab_compose, tab_batch, tab_analysis = st.tabs(["✉️ Single Message", "📂 Batch Process", "📊 Global Insights"])

# --- TAB 1: COMPOSE & SCAN ---
with tab_compose:
    input_sms = st.text_area("Analyze suspicious content...", placeholder="e.g. You've won a $1000 prize!", height=150)
    
    col_btn, _ = st.columns([1, 5])
    with col_btn:
        predict_btn = st.button("RUN FORENSIC ANALYSIS ⚡", use_container_width=True)
        
    if predict_btn and input_sms:
        transformed = transform_text(input_sms)
        vector = tfidf.transform([transformed])
        proba = model.predict_proba(vector)[0]
        result = 1 if proba[1] >= threshold else 0
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("<div class='stCard'>", unsafe_allow_html=True)
            if result == 1:
                st.markdown(f"<h2>🛑 THREAT DETECTED: <span class='spam-badge'>SPAM</span></h2>", unsafe_allow_html=True)
                st.error(f"High risk classification. Confidence Score: {proba[1]*100:.1f}%")
            else:
                st.markdown(f"<h2>✅ VERIFIED SECURE: <span class='ham-badge'>HAM</span></h2>", unsafe_allow_html=True)
                st.success(f"Message passed linguistic validation. Spam Probability: {proba[1]*100:.1f}%")
            st.progress(proba[1] if result == 1 else proba[0])
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div class='stCard'><h4>🚩 Detection Markers</h4></div>", unsafe_allow_html=True)
            spam_keywords = ['free', 'win', 'prize', 'urgent', 'claim', 'award', 'cash', 'gift', 'click', 'subscribe', 'call', 'money', 'apply', 'congratulations']
            found = [w for w in spam_keywords if w in input_sms.lower()]
            if found:
                for f in found: st.error(f"- **{f.upper()}** detected")
            else:
                st.info("No suspicious pattern markers detected.")

# --- TAB 2: BATCH PROCESSING ---
with tab_batch:
    st.subheader("Bulk Forensic Scanner")
    st.info("Upload communication logs for automated threat assessment.")
    uploaded_file = st.file_uploader("Drop CSV file here...", type=["csv", "txt"])
    
    if uploaded_file:
        df_uploader = pd.read_csv(uploaded_file)
        if 'text' in df_uploader.columns:
            if st.button("EXECUTE BATCH SCAN"):
                with st.spinner("Processing..."):
                    texts = df_uploader['text'].apply(transform_text)
                    vectors = tfidf.transform(texts)
                    probas = model.predict_proba(vectors)[:, 1]
                    df_uploader['Spam Probability'] = probas
                    df_uploader['Classification'] = np.where(probas >= threshold, 'Spam', 'Ham')
                    st.success("Batch Analysis Complete!")
                    st.dataframe(df_uploader.style.background_gradient(subset=['Spam Probability'], cmap='Reds'))
                    csv_output = df_uploader.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Forensic Report", csv_output, "spam_report.csv", "text/csv")
        else:
            st.error("Error: CSV must contain a 'text' column.")

# --- TAB 3: VISUAL ANALYTICS ---
with tab_analysis:
    st.subheader("Neural Network Insights")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**🔥 Threat Word Frequency**")
        spam_text = " ".join(dataset[dataset['target'] == 'spam']['text'])
        wc = WordCloud(width=800, height=400, background_color='#030014', colormap='Reds').generate(spam_text)
        fig, ax = plt.subplots(facecolor='#030014')
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
        
    with col_b:
        st.markdown("**📈 Engine Confidence Map**")
        all_probas = model.predict_proba(tfidf.transform(dataset['text'].head(500).apply(transform_text)))[:, 1]
        fig_hist = px.histogram(all_probas, nbins=20, title="Probability Distribution", color_discrete_sequence=['#6366F1'])
        fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_hist, use_container_width=True)

# Footer
st.markdown("<div style='text-align: center; color: grey; margin-top: 50px;'>SpamGuard Pro v4.2 | Intelligence Systems Division</div>", unsafe_allow_html=True)
                        <div style="margin-bottom:8px;">
                            {' '.join([f'<span class="trigger-tag">#{t}</span>' for t in found_tokens[:3]])}
                        </div>
                        <div class="safety-tip">
                            <i class="fas fa-shield-halved" style="color:{'#4ADE80' if not is_spam else '#FF6B6B'}"></i>
                            Recommendation: {'This message appears safe.' if not is_spam else 'Do not click links or provide details.'}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. FEATURE GRID ---
st.markdown("""
<div class="feature-grid">
    <div class="feature-card">
        <div class="feature-icon"><i class="fas fa-brain"></i></div>
        <h3>Pattern DNA</h3>
        <p>Analyzing structural entropy and token anomalies for instant identification.</p>
    </div>
    <div class="feature-card">
        <div class="feature-icon"><i class="fas fa-clock"></i></div>
        <h3>Zero Latency</h3>
        <p>No Python bridge required for Hero analysis. Pure JavaScript performance.</p>
    </div>
    <div class="feature-card">
        <div class="feature-icon"><i class="fas fa-lock"></i></div>
        <h3>Privacy-First</h3>
        <p>Inference runs entirely in your local browser memory. Data never leaves your device.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 8. FOOTER ---
st.markdown("<h2 style='text-align:center; font-family:Outfit; font-size:2.5rem; margin-bottom:4rem; color:white;'>SpamGuard Pro</h2>", unsafe_allow_html=True)

# --- 9. HIDDEN ADVANCED SUITE ---
with st.expander("🛠️ Internal Intelligence Dashboard (Advanced)"):
    tab1, tab2 = st.tabs(["📂 Batch Scan", "📊 Visuals"])
    with tab1:
        st.info("Upload communication logs for forensic auditing.")
    with tab2:
        st.info("Neural network insights and probability distributions.")
