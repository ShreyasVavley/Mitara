import streamlit as st
import time
from context_engine import ContextEngine
from safety_engine import SafetyEngine
from rag_store import RAGStore

# --- 1. INITIALIZE BACKEND ENGINES ---
# We cache this so ChromaDB doesn't re-initialize on every button click
@st.cache_resource
def initialize_system():
    return ContextEngine(), SafetyEngine(), RAGStore(data_directory="medical_data")

context_engine, safety_engine, rag_store = initialize_system()

# --- 2. FRONTEND UI STYLING (Hand-Drawn Theme) ---
st.set_page_config(page_title="Mitara AI Notepad", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@400;600;700&family=Patrick+Hand&display=swap');

    .stApp {
        background-color: #fdfbf7;
        background-image: linear-gradient(#fdfbf7 29px, #91d2fa 30px);
        background-size: 100% 30px;
        color: #2c3e50;
        font-family: 'Patrick Hand', cursive;
        font-size: 1.2rem;
    }
    
    * { font-family: 'Patrick Hand', cursive !important; }
    h1, h2, h3, h4 { font-family: 'Caveat', cursive !important; color: #2c3e50; letter-spacing: 1px; }
    
    .main-title {
        font-family: 'Caveat', cursive !important; font-size: 4rem; font-weight: 700;
        color: #2c3e50; text-align: center; margin-bottom: 0px;
        text-decoration: underline; text-decoration-style: wavy; text-decoration-color: #e74c3c;
    }
    .sub-title { color: #7f8c8d; text-align: center; font-size: 1.5rem; margin-bottom: 40px; }

    .sketch-card {
        background: #fdfbf7; border: 2px solid #2c3e50;
        border-radius: 255px 15px 225px 15px/15px 225px 15px 255px;
        padding: 25px; box-shadow: 6px 6px 0px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px; transition: transform 0.2s ease;
    }
    .sketch-card:hover { transform: rotate(-1deg); }
    .doctor-card { border-color: #2980b9; box-shadow: 6px 6px 0px rgba(41, 128, 185, 0.15); }

    .emergency-alert {
        border: 3px solid #c0392b; border-radius: 15px 225px 15px 255px/255px 15px 225px 15px;
        padding: 15px; color: #c0392b; font-family: 'Caveat', cursive !important;
        font-size: 1.8rem; font-weight: bold; margin-bottom: 20px;
        text-align: center; background: rgba(192, 57, 43, 0.05); transform: rotate(1deg);
    }
    .output-text { color: #34495e; font-size: 1.3rem; line-height: 1.8; padding: 15px; }
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
                time.sleep(1) # Dramatic pause
                
                # --- MONOLITHIC BACKEND LOGIC ---
                combined_text = f"{symptoms} {history} {meds}"
                is_emergency, safety_msg = safety_engine.evaluate_input(combined_text)
                
                if is_emergency:
                    data = {
                        'safety_flag': True,
                        'safety_message': safety_msg,
                        'patient_guidance': "Please seek emergency medical attention immediately.",
                        'doctor_brief': "URGENT: Patient reports critical symptoms indicative of a medical emergency.",
                        'requires_doctor_verification': True
                    }
                else:
                    context = context_engine.process_input(symptoms, history, meds, "")
                    query = " ".join([s.description for s in context.symptoms])
                    guidelines = rag_store.get_grounded_context(query)
                    
                    symptom_str = query if query else "the reported issues"
                    patient_guidance = f"We have logged your symptoms regarding '{symptom_str}'. Based on our initial scan, it is recommended to monitor your condition closely and consult with your physician. Stay hydrated and rest."
                    
                    history_str = ', '.join(context.history.conditions) if context.history.conditions else 'None reported'
                    meds_str = ', '.join(context.medications.current_medications) if context.medications.current_medications else 'None reported'
                    
                    doctor_brief = (
                        f"**CHIEF COMPLAINT:** {symptom_str.title()}\n"
                        f"**HISTORY:** {history_str}\n"
                        f"**MEDICATIONS:** {meds_str}\n\n"
                        f"**CLINICAL GUIDELINES RETRIEVED:**\n{guidelines}\n\n"
                        f"**PLAN:** Evaluate for standard protocol alignment.\n\n"
                        f"(Note: AI LLM is offline. Output generated via dynamic fallback logic.)"
                    )
                    
                    data = {
                        'safety_flag': False,
                        'safety_message': "Safe",
                        'patient_guidance': patient_guidance,
                        'doctor_brief': doctor_brief,
                        'requires_doctor_verification': True
                    }
                
                st.session_state['analysis'] = data
        else:
            st.warning("Please write down some symptoms first!")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    if 'analysis' in st.session_state:
        data = st.session_state['analysis']
        
        if data['safety_flag']:
            st.markdown(f'<div class="emergency-alert">🚨 {data["safety_message"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color: #27ae60; font-family: \'Caveat\', cursive !important; font-size: 1.5rem; margin-bottom: 10px;">✓ Patient seems stable (Safety Passed)</div>', unsafe_allow_html=True)
            
        st.markdown('<div class="sketch-card">', unsafe_allow_html=True)
        st.markdown("<h3>🗣️ What to tell the patient:</h3>", unsafe_allow_html=True)
        st.markdown(f'<div class="output-text">{data["patient_guidance"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
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
        st.markdown("""
        <div style="height: 100%; display: flex; align-items: center; justify-content: center; opacity: 0.5; margin-top: 100px;">
            <div style="text-align: center;">
                <h2 style="color: #7f8c8d; font-family: 'Caveat', cursive !important;">Waiting for patient notes...</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
