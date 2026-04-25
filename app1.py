import streamlit as st
import pandas as pd
import json
import os
import re
import tempfile
from groq import Groq
from streamlit_mic_recorder import mic_recorder
from fuzzywuzzy import fuzz

# --- 1. CONFIGURATION & THEME ---
st.set_page_config(
    page_title="FormSathi AI | Digital Bharat",
    page_icon="Weblogo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Groq
GROQ_API_KEY = ""

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

if not GROQ_API_KEY:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# --- 2. MULTILINGUAL ASSETS (SIMPLE BHARAT HINDI) ---
L_DATA = {
    "en": {
        "title": "FormSathi AI",
        "tagline": "Simple help for Government Schemes",
        "profile_hdr": "👤 Your Profile",
        "name": "Full Name",
        "age": "Age",
        "gender": "Gender",
        "cat": "Category (Caste)",
        "inc": "Yearly Income (₹)",
        "occ": "Occupation",
        "state": "State",
        "area": "Area Type",
        "dis": "Disability?",
        "aadhaar": "Aadhaar Number (Optional)",
        "aadhaar_note": "XXXX-XXXX-1234 (Used only for check)",
        "mic_btn": "🎙️ Speak your need",
        "stop_btn": "⏹️ Stop",
        "search_ph": "E.g. 'I need help with hospital bills'...",
        "eligible": "✅ Eligible",
        "maybe": "⚠️ Maybe",
        "no": "❌ Not Eligible",
        "apply": "Apply Now",
        "docs": "Documents Required",
        "why": "Reason",
        "offline_warn": "⚠️ Offline Mode: Basic results only",
        "privacy": "🔒 Your data is safe and not stored permanently.",
        "step_1": "Tell your need",
        "step_2": "See schemes",
        "step_3": "Get benefits"
    },
    "hi": {
        "title": "फॉर्मसाथी AI",
        "tagline": "सरकारी योजनाओं की आसान जानकारी",
        "profile_hdr": "👤 आपकी जानकारी",
        "name": "पूरा नाम",
        "age": "उम्र",
        "gender": "लिंग",
        "cat": "वर्ग (Category)",
        "inc": "सालाना कमाई (₹)",
        "occ": "काम/व्यवसाय",
        "state": "राज्य",
        "area": "क्षेत्र",
        "dis": "विकलांगता?",
        "aadhaar": "आधार नंबर (वैकल्पिक)",
        "aadhaar_note": "XXXX-XXXX-1234 (केवल जांच के लिए)",
        "mic_btn": "🎙️ बोलकर पूछें",
        "stop_btn": "⏹️ रुकें",
        "search_ph": "जैसे: 'मुझे अस्पताल के लिए मदद चाहिए'...",
        "eligible": "✅ आप पात्र हैं",
        "maybe": "⚠️ शायद पात्र",
        "no": "❌ पात्र नहीं",
        "apply": "अभी आवेदन करें",
        "docs": "जरूरी कागज",
        "why": "कारण",
        "offline_warn": "⚠️ ऑफलाइन मोड: सीमित जानकारी",
        "privacy": "🔒 आपकी जानकारी सुरक्षित है और कहीं सहेजी नहीं जाती।",
        "step_1": "जरूरत बताएं",
        "step_2": "योजना देखें",
        "step_3": "फायदा उठाएं"
    }
}

# --- 3. SCHEME MASTER DATA ---
@st.cache_data
def get_schemes():
    return [
        {"id": 1, "name": "PM-KISAN", "cat": ["General", "OBC", "SC", "ST"], "gen": "All", "inc_max": 200000, "occ": "Farmer", "ben": "₹6,000 yearly directly in bank", "docs": "Aadhaar, Land Papers", "tags": "kheti, farmer, money, paisa", "url": "pmkisan.gov.in"},
        {"id": 2, "name": "Ayushman Bharat", "cat": ["General", "OBC", "SC", "ST"], "gen": "All", "inc_max": 500000, "occ": "All", "ben": "₹5 Lakh free hospital treatment", "docs": "Ration Card, Aadhaar", "tags": "hospital, doctor, health, bimari", "url": "pmjay.gov.in"},
        {"id": 3, "name": "PM SVANidhi", "cat": ["General", "OBC", "SC", "ST"], "gen": "All", "inc_max": 100000, "occ": "Business", "ben": "₹10,000 loan for street vendors", "docs": "Vendor ID, Aadhaar", "tags": "loan, dukaan, shop, street", "url": "pmsvanidhi.mohua.gov.in"},
        {"id": 4, "name": "Ujjwala 2.0", "cat": ["General", "OBC", "SC", "ST"], "gen": "Female", "inc_max": 200000, "occ": "All", "ben": "Free Gas connection & Cylinder", "docs": "BPL Card, Aadhaar", "tags": "gas, cylinder, cooking", "url": "pmuy.gov.in"},
        {"id": 5, "name": "PM Mudra Loan", "cat": ["General", "OBC", "SC", "ST"], "gen": "All", "inc_max": 1500000, "occ": "Business", "ben": "Collateral-free loan up to 10L", "docs": "Business Plan, ID Proof", "tags": "loan, startup, business", "url": "mudra.org.in"},
        {"id": 6, "name": "Sukanya Samriddhi", "cat": ["General", "OBC", "SC", "ST"], "gen": "Female", "inc_max": 10000000, "occ": "All", "ben": "High interest savings for daughters", "docs": "Birth Cert, Aadhaar", "tags": "beti, daughter, savings", "url": "nsiindia.gov.in"}
    ]

# --- 4. CORE ENGINE FUNCTIONS ---

def check_eligibility(scheme, profile, L):
    score = 100
    reasons = []

    if profile['income'] > scheme['inc_max']:
        score -= 40
        reasons.append("Income too high")

    if scheme['gen'] != "All" and profile['gender'] != scheme['gen']:
        score -= 30
        reasons.append("Gender mismatch")

    if scheme['occ'] != "All" and profile['occupation'] != scheme['occ']:
        score -= 20
        reasons.append("Occupation mismatch")

    if profile['category'] not in scheme['cat']:
        score -= 30
        reasons.append("Category mismatch")

    if score >= 70:
        status = L["eligible"]
        color = "#28a745"
    elif score >= 40:
        status = L["maybe"]
        color = "#ffc107"
    else:
        status = L["no"]
        color = "#dc3545"

    return status, ", ".join(reasons) or "Perfect match", color

def get_rule_results(query):
    """Offline-first keyword search."""
    db = get_schemes()
    matches = []
    query = query.lower()
    for s in db:
        score = fuzz.partial_token_set_ratio(query, (s['name'] + s['tags']).lower())
        if score > 60: matches.append(s)
    return matches[:3]

def get_ai_response(query, profile, lang):
    """Groq Llama-3 intelligence layer."""
    if not client: return get_rule_results(query), "Offline Mode"
    
    db = get_schemes()
    sys_prompt = f"""
    You are a Bharat Government Scheme Assistant.

    STRICT RULE:
    - Respond ONLY in {lang}
    - If Hindi → use simple Hindi
    - If English → use simple English
    - No mixing languages

    User Profile:
    {profile}

    Return JSON:
    {{
     'msg': 'short explanation in selected language',
     'ids': [scheme_ids]
    }}
    """    
    try:
        res = client.chat.completions.create(
            messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": query}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"},
            timeout=5
        )
        data = json.loads(res.choices[0].message.content)
        matches = [s for s in db if s['id'] in data.get('ids', [])]
        return matches, data.get('msg', "")
    except:
        return get_rule_results(query), "Network slow, using basic matching."

# --- 5. BHARAT PREMIUM UI (CSS) ---

def apply_ui_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Outfit', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #E0EAFC 0%, #CFDEF3 100%);
    }

    /* Glassmorphic Profile Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.3) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255,255,255,0.2);
    }

    /* Professional Scheme Card */
    .scheme-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(15px);
        border-radius: 24px;
        padding: 30px;
        border: 1px solid rgba(255,255,255,0.4);
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        transition: 0.3s transform ease;
    }
    .scheme-card:hover { transform: translateY(-5px); }

    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none; padding: 10px; font-weight: 700;
    }

    .status-pill {
        padding: 5px 15px; border-radius: 50px; font-size: 0.8rem; 
        font-weight: 700; color: white; display: inline-block; margin-bottom: 15px;
    }
    
    .hero-title {
        background: linear-gradient(45deg, #06038D, #FF9933);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 3rem; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 6. MAIN APP FLOW ---

def main():
    apply_ui_styles()
    
    if "lang" not in st.session_state: st.session_state.lang = "en"
    L = L_DATA[st.session_state.lang]

    # --- SIDEBAR: ADVANCED PROFILE ---
    with st.sidebar:
        st.session_state.lang = st.radio("Language / भाषा", ["en", "hi"], horizontal=True)
        st.markdown(f"## {L['profile_hdr']}")
        u_name = st.text_input(L['name'], placeholder="Citizen")
        
        c1, c2 = st.columns(2)
        u_age = c1.number_input(L['age'], 1, 100, 25)
        u_gen = c2.selectbox(L['gender'], ["Male", "Female", "Other"])
        
        u_cat = st.selectbox(L['cat'], ["General", "OBC", "SC", "ST"])
        u_inc = st.number_input(L['inc'], 0, 10000000, 180000)
        u_occ = st.selectbox(L['occ'], ["Farmer", "Student", "Worker", "Business", "Unemployed"])
        
        u_state = st.selectbox(L['state'], ["Delhi", "Maharashtra", "UP", "Bihar", "Karnataka", "Other"])
        u_area = st.radio(L['area'], ["Rural", "Urban"], horizontal=True)
        u_dis = st.radio(L['dis'], ["No", "Yes"], horizontal=True)
        
        u_aadhaar = st.text_input(L['aadhaar'], type="password", max_chars=12, help=L['aadhaar_note'])
        st.caption(L['privacy'])
        
        user_profile = {
            "name": u_name, "age": u_age, "gender": u_gen, "category": u_cat,
            "income": u_inc, "occupation": u_occ, "state": u_state, "disability": u_dis
        }

    # --- MAIN CONTENT ---
    st.markdown(f"<h1 class='hero-title'>{L['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#555;'>{L['tagline']}</p>", unsafe_allow_html=True)

    # Voice & Input Section
    col_mic, col_in = st.columns([1, 5])
    with col_mic:
        st.write(" ") # padding
        audio = mic_recorder(start_prompt=L['mic_btn'], stop_prompt=L['stop_btn'], key='mic_recorder')
    
    with col_in:
        query = st.chat_input(L['search_ph'])

    # Voice Processing
    if audio:
        with st.spinner("समझ रहे हैं..."):            
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio['bytes'])
                    tmp_path = tmp.name
                with open(tmp_path, "rb") as f:
                    ts = client.audio.transcriptions.create(file=(tmp_path, f.read()), model="distil-whisper-large-v3-en", response_format="text")
                query = ts
                os.remove(tmp_path)
            except: st.error("Voice Error. Try typing!")

    # Search Logic
    if query:
        st.markdown(f"### 🗨️ {query}")
        with st.spinner("🤖 Searching Bharat Databases..."):
            schemes, ai_msg = get_ai_response(query, user_profile, st.session_state.lang)
            st.info(ai_msg if ai_msg else "Matching best results...")

            if not schemes:
                st.warning("No matches found. Showing general popular schemes.")
                schemes = get_schemes()[:2]

            for s in schemes:
                status, reason, color = check_eligibility(s, user_profile, L)
                
                st.markdown(f"""
                <div class="scheme-card">
                    <div class="status-pill" style="background:{color};">{status}</div>
                    <h2 style="margin:0; color:#06038D;">{s['name']}</h2>
                    <p style="font-size:1.1rem; font-weight:500; color:#138808; margin:10px 0;">💰 Benefit: {s['ben']}</p>
                    <p style="color:#666;"><b>{L['why']}:</b> {reason}</p>
                    <hr style="opacity:0.2;">
                    <p>📄 <b>{L['docs']}:</b> {s['docs']}</p>
                </div>
                """, unsafe_allow_html=True)
                st.link_button(f"🔗 {L['apply']}: {s['name']}", f"https://{s['url']}")

    # Onboarding UI
    if not query:
        cols = st.columns(3)
        icons = ["🧑", "🔎", "✅"]
        for i, col in enumerate(cols):
            with col:
                st.markdown(f"""
                <div style="text-align:center; background:white; padding:20px; border-radius:20px;">
                    <h1 style="margin:0;">{icons[i]}</h1>
                    <b>Step {i+1}</b><br>{L[f'step_{i+1}']}
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()