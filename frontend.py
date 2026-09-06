import streamlit as st
import requests
import time

# Hand-Drawn "Doctor's Notepad" Styling
st.set_page_config(page_title="Mitara AI Notepad", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@400;600;700&family=Patrick+Hand&display=swap');

    /* Global App Background - Ruled Notebook Paper */
    .stApp {
        background-color: #fdfbf7;
        background-image: 
            linear-gradient(#fdfbf7 29px, #91d2fa 30px);
        background-size: 100% 30px;
        color: #2c3e50;
        font-family: 'Patrick Hand', cursive;
        font-size: 1.2rem;
    }
    
    /* Global Typography Override */
    * {
        font-family: 'Patrick Hand', cursive !important;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Caveat', cursive !important;
        color: #2c3e50;
        letter-spacing: 1px;
    }
    
    /* Main Title Handwritten Text */
    .main-title {
        font-family: 'Caveat', cursive !important;
        font-size: 4rem;
        font-weight: 700;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 0px;
        text-decoration: underline;
        text-decoration-style: wavy;
        text-decoration-color: #e74c3c;
    }
    .sub-title {
        color: #7f8c8d;
        text-align: center;
        font-size: 1.5rem;
        margin-bottom: 40px;
    }

    /* Hand-Drawn Sketch Cards */
    .sketch-card {
        background: #fdfbf7;
        border: 2px solid #2c3e50;
        /* Classic CSS trick for irregular hand-drawn borders */
        border-radius: 255px 15px 225px 15px/15px 225px 15px 255px;
        padding: 25px;
        box-shadow: 6px 6px 0px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
        transition: transform 0.2s ease;
    }
    .sketch-card:hover {
        transform: rotate(-1deg);
    }
    
    .doctor-card {
        border-color: #2980b9;
        box-shadow: 6px 6px 0px rgba(41, 128, 185, 0.15);
    }

    /* Red Ink Emergency Alert */
    .emergency-alert {
        border: 3px solid #c0392b;
        border-radius: 15px 225px 15px 255px/255px 15px 225px 15px;
        padding: 15px;
        color: #c0392b;
        font-family: 'Caveat', cursive !important;
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 20px;
        text-align: center;
        background: rgba(192, 57, 43, 0.05);
        transform: rotate(1deg);
    }

    /* Handwritten Output Text Formatting */
    .output-text {
        color: #34495e;
        font-size: 1.3rem;
        line-height: 1.8;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">Mitara AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Clinical Decision-Support Notepad</div>', unsafe_allow_html=True)

# Columns Layout
col1, col2, col3 = st.columns([1.2, 0.1, 1.5])

with col1:
    st.markdown('<div class="sketch-card">', unsafe_allow_html=True)
    st.markdown("<h3>📝 Patient Context</h3>", unsafe_allow_html=True)
    
    symptoms = st.text_area("Symptoms:", placeholder="What is the patient feeling?", height=100)
    history = st.text_input("Medical History:", placeholder="Past conditions...")
    meds = st.text_input("Medications:", placeholder="Current meds...")
    
    if st.button("Scribble Analysis", type="primary", use_container_width=True):
        if symptoms:
            with st.spinner("Flipping through medical books..."):
                time.sleep(0.5) 
                payload = {
                    "symptoms_text": symptoms,
                    "history_text": history,
                    "meds_text": meds,
                    "transcript": ""
                }
                
                try:
                    response = requests.post("http://localhost:8000/analyze", json=payload)
                    response.raise_for_status()
                    st.session_state['analysis'] = response.json()
                except Exception as e:
                    st.error(f"Uh oh! Backend is unplugged: {e}")
        else:
            st.warning("Please write down some symptoms first!")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    if 'analysis' in st.session_state:
        data = st.session_state['analysis']
        
        # Safety Engine Top Block
        if data['safety_flag']:
            st.markdown(f'<div class="emergency-alert">🚨 {data["safety_message"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color: #27ae60; font-family: \'Caveat\', cursive !important; font-size: 1.5rem; margin-bottom: 10px;">✓ Patient seems stable (Safety Passed)</div>', unsafe_allow_html=True)
            
        # Patient Output Card
        st.markdown('<div class="sketch-card">', unsafe_allow_html=True)
        st.markdown("<h3>🗣️ What to tell the patient:</h3>", unsafe_allow_html=True)
        st.markdown(f'<div class="output-text">{data["patient_guidance"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Doctor Output Card
        st.markdown('<div class="sketch-card doctor-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='color: #2980b9;'>🩺 Doctor's Clinical Notes:</h3>", unsafe_allow_html=True)
        formatted_brief = data['doctor_brief'].replace('\n', '<br>')
        st.markdown(f'<div class="output-text" style="color: #2980b9;">{formatted_brief}</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if data['requires_doctor_verification']:
            st.info("Doctor: Please sign off on these notes.")
            if st.button("Sign & Approve"):
                st.success("Signed by Physician! Notes added to file.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Standby state
        st.markdown("""
        <div style="height: 100%; display: flex; align-items: center; justify-content: center; opacity: 0.5; margin-top: 100px;">
            <div style="text-align: center;">
                <h2 style="color: #7f8c8d; font-family: 'Caveat', cursive !important;">Waiting for patient notes...</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
