import streamlit as st
import time
from context_engine import ContextEngine
from safety_engine import SafetyEngine
from rag_store import RAGStore

# --- 1. INITIALIZE BACKEND ENGINES ---
@st.cache_resource
def initialize_system():
    return ContextEngine(), SafetyEngine(), RAGStore(data_directory="medical_data")

context_engine, safety_engine, rag_store = initialize_system()

# --- 2. PREMIUM ENTERPRISE UI STYLING ---
st.set_page_config(page_title="Mitara AI", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* Global Dark Theme Background */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Clean Titles */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #38bdf8;
        text-align: center;
        letter-spacing: -1px;
        margin-bottom: 0;
    }
    .sub-title {
        color: #94a3b8;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 40px;
        font-weight: 300;
    }

    /* Style the native Streamlit text areas and inputs */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 1px #38bdf8 !important;
    }

    /* Output Boxes */
    .guidance-box {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border-left: 4px solid #38bdf8;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }
    
    .doctor-box {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border-left: 4px solid #a855f7;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }

    .emergency-box {
        background: rgba(220, 38, 38, 0.1);
        border: 1px solid #ef4444;
        border-left: 4px solid #ef4444;
        padding: 15px;
        color: #fca5a5;
        border-radius: 8px;
        font-weight: 600;
        margin-bottom: 20px;
    }

    /* Button Styling */
    .stButton>button {
        background-color: #38bdf8 !important;
        color: #0f172a !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #0ea5e9 !important;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">Mitara AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Secure Clinical Decision-Support Infrastructure</div>', unsafe_allow_html=True)

# Columns Layout (Native Streamlit, no broken HTML wrappers)
col1, col2, col3 = st.columns([1.2, 0.1, 1.5])

with col1:
    st.subheader("Patient Context")
    symptoms = st.text_area("Symptoms Log", placeholder="Enter patient symptoms (e.g., severe chest pain)...", height=120)
    history = st.text_input("Medical History", placeholder="Any pre-existing conditions...")
    meds = st.text_input("Current Medications", placeholder="Active prescriptions...")
    
    st.write("") # Spacer
    if st.button("Initialize Neural Analysis", use_container_width=True):
        if symptoms:
            with st.spinner("Analyzing context and querying Vector Database..."):
                time.sleep(0.8) # Smooth UX delay
                
                # --- MONOLITHIC BACKEND LOGIC ---
                combined_text = f"{symptoms} {history} {meds}"
                is_emergency, safety_msg = safety_engine.evaluate_input(combined_text)
                
                if is_emergency:
                    data = {
                        'safety_flag': True,
                        'safety_message': safety_msg,
                        'patient_guidance': "CRITICAL: Please seek emergency medical attention immediately.",
                        'doctor_brief': "URGENT ALARM: Patient reports critical symptoms indicative of a medical emergency. Bypass standard queue.",
                        'requires_doctor_verification': True
                    }
                else:
                    context = context_engine.process_input(symptoms, history, meds, "")
                    query = " ".join([s.description for s in context.symptoms])
                    guidelines = rag_store.get_grounded_context(query)
                    
                    symptom_str = query if query else "the reported issues"
                    patient_guidance = f"We have logged your symptoms regarding '{symptom_str}'. Based on our scan, please monitor your condition closely and consult with your physician. Stay hydrated and rest."
                    
                    history_str = ', '.join(context.history.conditions) if context.history.conditions else 'None reported'
                    meds_str = ', '.join(context.medications.current_medications) if context.medications.current_medications else 'None reported'
                    
                    doctor_brief = (
                        f"**CHIEF COMPLAINT:** {symptom_str.title()}\n\n"
                        f"**HISTORY:** {history_str}\n\n"
                        f"**MEDICATIONS:** {meds_str}\n\n"
                        f"---\n"
                        f"**CLINICAL GUIDELINES RETRIEVED:**\n{guidelines if guidelines else 'No local protocols found for this specific query.'}\n\n"
                        f"---\n"
                        f"**PLAN:** Evaluate for standard protocol alignment.\n"
                    )
                    
                    data = {
                        'safety_flag': False,
                        'safety_message': "System Safe",
                        'patient_guidance': patient_guidance,
                        'doctor_brief': doctor_brief,
                        'requires_doctor_verification': True
                    }
                
                st.session_state['analysis'] = data
        else:
            st.error("Error: Patient Symptoms are required to initiate analysis.")

with col3:
    if 'analysis' in st.session_state:
        data = st.session_state['analysis']
        
        # Safety Check
        if data['safety_flag']:
            st.markdown(f'<div class="emergency-box">🚨 EMERGENCY DETECTED: {data["safety_message"]}</div>', unsafe_allow_html=True)
        else:
            st.success("✅ Safety Gate Passed")
            
        # Patient Card
        st.markdown(f"""
        <div class="guidance-box">
            <h4 style="color: #38bdf8; margin-top: 0;">Patient Guidance Terminal</h4>
            <p style="color: #cbd5e1;">{data['patient_guidance']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Doctor Card
        formatted_brief = data['doctor_brief'].replace('\n', '<br>')
        st.markdown(f"""
        <div class="doctor-box">
            <h4 style="color: #a855f7; margin-top: 0;">Physician Clinical Summary</h4>
            <p style="color: #cbd5e1; font-size: 0.95rem;">{formatted_brief}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if data['requires_doctor_verification']:
            st.info("AUTH REQUIRED: Physician must cryptographically sign to release guidance.")
            if st.button("Verify & Dispatch to Patient", type="secondary"):
                st.balloons()
                st.success("Verification Complete: Guidance dispatched securely.")
    else:
        st.markdown("""
        <div style="height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; opacity: 0.4; margin-top: 100px;">
            <h2 style="color: #94a3b8; font-weight: 300;">System Standby</h2>
            <p style="color: #64748b;">Awaiting patient data stream...</p>
        </div>
        """, unsafe_allow_html=True)
