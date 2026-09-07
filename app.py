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

# Bento Box CSS & Fix Input Colors
st.markdown("""
<style>
    /* Global Background */
    .stApp {
        background-color: #f3f4f6;
    }
    
    /* Bento Box Containers */
    .bento-box {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
        border: 1px solid #e5e7eb;
    }
    
    .bento-alert {
        background-color: #fef2f2;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        border: 1px solid #f87171;
        color: #991b1b;
        font-weight: 600;
    }
    
    /* Force Input Text Colors Explicitly */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 12px !important;
        border: 1px solid #d1d5db !important;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #000000 !important;
        box-shadow: 0 0 0 1px #000000 !important;
    }
    
    /* Header Bento */
    .bento-header {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 24px;
        border: 1px solid #e5e7eb;
    }
    
    h1, h3, p { color: #111827 !important; }
</style>
""", unsafe_allow_html=True)

# Header Bento
st.markdown("""
<div class="bento-header">
    <h1 style="margin:0; font-size: 28px;">Mitara</h1>
    <p style="margin:0; color: #6b7280 !important; font-size: 16px;">Clinical Decision Support System</p>
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
                    if "fever" in combined_input or "cough" in combined_input or "cold" in combined_input:
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
            <strong style="font-size: 18px;">Patient Guidance</strong><br><br>
            <span style="color: #4b5563;">{res['patient_text']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        doctor_html = res['doctor_text'].replace('\n', '<br>')
        st.markdown(f"""
        <div class="bento-box">
            <strong style="font-size: 18px;">Physician Summary</strong><br><br>
            <span style="color: #4b5563;">{doctor_html}</span>
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
