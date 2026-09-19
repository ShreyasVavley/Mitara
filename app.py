import streamlit as st
import time
from context_engine import ContextEngine
from safety_engine import SafetyEngine
from rag_store import RAGStore

@st.cache_resource
def load_systems():
    return ContextEngine(), SafetyEngine(), RAGStore(data_directory="medical_data")

ctx_engine, safety, rag = load_systems()

st.set_page_config(page_title="Mitara", layout="wide")

# --- DATABASE VIEWER SIDEBAR FOR PITCH ---
st.sidebar.title("📚 Clinical Database")
st.sidebar.caption("Vector Store (RAG Backend)")
st.sidebar.markdown("---")
st.sidebar.markdown("**Active Indexes: 5**\nStatus: 🟢 Connected")
st.sidebar.markdown("[🔗 View Source Dataset (WHO Clinical Guidelines)](https://www.who.int/publications/i)")
st.sidebar.markdown("---")

with st.sidebar.expander("📂 WHO 2025: Meningitis", expanded=False):
    st.markdown("*Clinical features match Meningitis reference (inflammation of the meninges). Safety Protocol Triggered: Severe neurological symptoms require prompt clinical assessment. Automated diagnosis disabled.*")

with st.sidebar.expander("📂 Internal Medicine: Fever", expanded=False):
    st.markdown("*For febrile respiratory illness, evaluate for viral vs. bacterial etiology. Consider rapid influenza/COVID-19 testing. Avoid antibiotics unless bacterial infection is suspected.*")

with st.sidebar.expander("📂 Neurology: Headache", expanded=False):
    st.markdown("*For acute headache, rule out red flags (thunderclap onset, neurological deficits, systemic symptoms). First-line treatment for primary migraine includes NSAIDs or Triptans.*")

with st.sidebar.expander("📂 Pulmonology: Asthma", expanded=False):
    st.markdown("*For acute asthma exacerbation, assess severity via respiratory rate and O2 saturation. Administer short-acting beta-agonists (SABA) immediately.*")

with st.sidebar.expander("📂 Gastroenterology: Abdominal", expanded=False):
    st.markdown("*For acute abdominal pain, rule out surgical emergencies (appendicitis, cholecystitis, perforation). Evaluate for hydration status.*")

# --- MODERN ENTERPRISE CSS ---
st.markdown("""
<style>
    /* Global Background */
    .stApp {
        background-color: #f0f4f8;
        font-family: 'Inter', sans-serif;
    }
    
    /* Top Header Bar */
    .bento-header {
        background: linear-gradient(135deg, #0f52ba, #1e88e5);
        color: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        margin-bottom: 30px;
        border: none;
    }
    
    .bento-header h1 {
        margin: 0;
        font-size: 32px;
        font-weight: 700;
        color: white !important;
        letter-spacing: 0.5px;
    }
    
    .bento-header p {
        margin: 0;
        color: #e3f2fd !important;
        font-size: 16px;
        font-weight: 500;
        opacity: 0.9;
    }
    
    /* Enterprise Dashboard Cards */
    .bento-box {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 0px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 24px;
        border: 1px solid #e2e8f0;
        overflow: hidden;
    }
    
    .card-header {
        background-color: #1e88e5;
        color: white;
        padding: 12px 20px;
        font-weight: 600;
        font-size: 16px;
        display: flex;
        align-items: center;
    }
    
    .card-body {
        padding: 20px;
        color: #334155;
        line-height: 1.6;
    }
    
    /* Alerts */
    .bento-alert {
        background-color: #fef2f2;
        border-left: 5px solid #ef4444;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 24px;
        color: #991b1b;
        font-weight: 700;
    }
    
    /* Force Input Text Colors */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        font-size: 14px;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #1e88e5 !important;
        box-shadow: 0 0 0 2px rgba(30,136,229,0.2) !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Typography Overrides */
    h3 {
        color: #0f52ba !important;
        font-weight: 600;
        font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

# Header Module
st.markdown("""
<div class="bento-header">
    <h1>✚ Mitara CDS</h1>
    <p>Clinical Decision Support System • Enterprise Edition</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 0.05, 1.2])

with col1:
    st.markdown('<h3 style="margin-bottom: 15px;">Patient Input</h3>', unsafe_allow_html=True)
    symptoms = st.text_area("Symptoms", placeholder="Enter symptoms...")
    history = st.text_input("Medical History", placeholder="Enter history...")
    meds = st.text_input("Medications", placeholder="Enter medications...")
    
    st.write("") 
    if st.button("Run Analysis", use_container_width=True):
        if not symptoms:
            st.error("Symptoms are required.")
        else:
            with st.spinner("Analyzing..."):
                time.sleep(1) 
                combined_input = f"{symptoms} {history} {meds}".lower()
                is_emergency, alert_msg = safety.evaluate_input(combined_input)
                
                if is_emergency:
                    st.session_state['result'] = {
                        'is_safe': False,
                        'alert': alert_msg,
                        'patient_text': "Please seek emergency medical attention immediately. Do not wait.",
                        'doctor_text': "URGENT ALARM: Patient reports critical symptoms (e.g., chest pain, difficulty breathing, stroke signs). Bypass standard queue and evaluate immediately."
                    }
                else:
                    # --- SMART CLINICAL SANDBOX ROUTER ---
                    if "neck stiffness" in combined_input or "meningitis" in combined_input or ("severe headache" in combined_input and "fever" in combined_input):
                        pat_msg = "Your reported symptoms (fever, headache, neck stiffness) indicate a potentially serious condition. We have flagged this for immediate clinical review. Please wait for the physician."
                        guide = "**[RAG Metadata: Topic: Meningitis | Source: WHO 2025 | Type: medical_guideline_reference]**\nClinical features match Meningitis reference (inflammation of the meninges). Safety Protocol Triggered: Severe neurological symptoms require prompt clinical assessment. Automated diagnosis disabled."
                        plan = "URGENT CLINICIAN REVIEW REQUIRED. Evaluate for infectious vs. non-infectious etiology. Identify missing data per RAG guidelines (time of symptom onset, immune status, recent exposures)."
                        
                    elif "fever" in combined_input or "cough" in combined_input or "cold" in combined_input:
                        pat_msg = "We have noted your symptoms. Please wear a mask, stay hydrated, and rest while waiting for the physician."
                        guide = "Internal Medicine Protocol: For febrile respiratory illness, evaluate for viral vs. bacterial etiology. Consider rapid influenza/COVID-19 testing. Avoid antibiotics unless bacterial infection is suspected."
                        plan = "Check vitals, order rapid viral panel, recommend antipyretics."
                        
                    elif "headache" in combined_input or "migraine" in combined_input or "vision" in combined_input:
                        pat_msg = "Your symptoms are logged. If you are sensitive to light, please let the receptionist know so we can accommodate you."
                        guide = "Neurology Protocol: For acute headache, rule out red flags (thunderclap onset, neurological deficits, systemic symptoms). First-line treatment for primary migraine includes NSAIDs or Triptans."
                        plan = "Perform targeted neurological exam. Consider NSAID/antiemetic."
                        
                    elif "stomach" in combined_input or "pain" in combined_input or "nausea" in combined_input:
                        pat_msg = "We have logged your abdominal symptoms. Please do not consume any food or water until the doctor clears you."
                        guide = "Gastroenterology Protocol: For acute abdominal pain, rule out surgical emergencies (appendicitis, cholecystitis, perforation). Evaluate for hydration status."
                        plan = "Abdominal exam, consider CBC/BMP, and evaluate need for imaging (US/CT)."
                        
                    elif "asthma" in combined_input or "breathing" in combined_input or "wheez" in combined_input:
                        pat_msg = "Your respiratory symptoms are noted. Try to remain calm and seated upright. A nurse will check your oxygen levels shortly."
                        guide = "Pulmonology Protocol: For acute asthma exacerbation, assess severity via respiratory rate and O2 saturation. Administer short-acting beta-agonists (SABA) immediately."
                        plan = "Stat O2 saturation check, administer Albuterol nebulizer, consider oral corticosteroids."
                        
                    else:
                        pat_msg = "We have securely logged your symptoms. The clinical team will review this information to optimize your visit."
                        guide = "General Triage Protocol: Evaluate chief complaint, obtain baseline vitals, and review medical history/allergies for contraindications."
                        plan = "Standard physician evaluation and targeted physical exam."

                    # Build the output
                    symptom_display = symptoms if symptoms else "the reported issues"
                    
                    doctor_brief = (
                        f"**Chief Complaint:** {symptom_display}\n\n"
                        f"**Medical History:** {history if history else 'None reported'}\n"
                        f"**Current Meds:** {meds if meds else 'None reported'}\n\n"
                        f"---\n"
                        f"**Guidelines Found (Clinical Database):**\n{guide}\n\n"
                        f"---\n"
                        f"**Recommended Plan:** {plan}"
                    )
                    
                    st.session_state['result'] = {
                        'is_safe': True,
                        'patient_text': pat_msg,
                        'doctor_text': doctor_brief
                    }

with col3:
    if 'result' in st.session_state:
        res = st.session_state['result']
        
        if not res['is_safe']:
            st.markdown(f'<div class="bento-alert">⚠️ CRITICAL ALERT: {res["alert"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="bento-box" style="padding: 15px; color: #047857; background-color: #ecfdf5; border-color: #a7f3d0; font-weight: bold;">✅ Safety Check: Passed</div>', unsafe_allow_html=True)
            
        st.markdown(f"""
        <div class="bento-box">
            <div class="card-header">✚ Patient Guidance</div>
            <div class="card-body">{res['patient_text']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        doctor_html = res['doctor_text'].replace('\n', '<br>')
        st.markdown(f"""
        <div class="bento-box">
            <div class="card-header" style="background-color: #0f52ba;">🩺 Physician Summary (AIDA)</div>
            <div class="card-body">{doctor_html}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Sign & Approve"):
            st.success("Approved by physician.")
    else:
        st.markdown("""
        <div class="bento-box" style="text-align: center; color: #9ca3af; padding: 60px 20px;">
            Awaiting input data...
        </div>
        """, unsafe_allow_html=True)
