import streamlit as st
import time
from context_engine import ContextEngine
from safety_engine import SafetyEngine
from rag_store import RAGStore

# Cache the initialization so it doesn't reload the DB every time
@st.cache_resource
def load_systems():
    return ContextEngine(), SafetyEngine(), RAGStore(data_directory="medical_data")

ctx_engine, safety, rag = load_systems()

st.set_page_config(page_title="Mitara AI", layout="wide")

# Simple Black & White styling
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    h1, h2, h3, h4, p, label {
        color: #000000 !important;
    }
    .stButton>button {
        background-color: #000000;
        color: #ffffff;
        border: 1px solid #000000;
        border-radius: 0px;
    }
    .stButton>button:hover {
        background-color: #333333;
        color: #ffffff;
        border: 1px solid #333333;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #000000;
        border-radius: 0px;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #000000 !important;
        box-shadow: none !important;
    }
    .output-box {
        border: 1px solid #000000;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #ffffff;
    }
    .alert-box {
        border: 2px solid #000000;
        padding: 15px;
        font-weight: bold;
        margin-bottom: 20px;
        background-color: #f8f9fa;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

st.title("Mitara AI")
st.markdown("Clinical Decision Support System")
st.markdown("---")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("Patient Input")
    symptoms = st.text_area("Symptoms", placeholder="Enter symptoms...")
    history = st.text_input("Medical History", placeholder="Enter history...")
    meds = st.text_input("Medications", placeholder="Enter medications...")
    
    st.write("") 
    if st.button("Run Analysis"):
        if not symptoms:
            st.error("Symptoms are required.")
        else:
            with st.spinner("Analyzing..."):
                time.sleep(1) 
                
                combined_input = f"{symptoms} {history} {meds}"
                is_emergency, alert_msg = safety.evaluate_input(combined_input)
                
                if is_emergency:
                    st.session_state['result'] = {
                        'is_safe': False,
                        'alert': alert_msg,
                        'patient_text': "Please seek emergency medical attention immediately.",
                        'doctor_text': "URGENT: Patient reports critical symptoms. Evaluate immediately."
                    }
                else:
                    parsed_context = ctx_engine.process_input(symptoms, history, meds, "")
                    search_query = " ".join([s.description for s in parsed_context.symptoms])
                    retrieved_docs = rag.get_grounded_context(search_query)
                    
                    symptom_display = search_query if search_query else "the reported issues"
                    
                    st.session_state['result'] = {
                        'is_safe': True,
                        'patient_text': f"We have noted your symptoms regarding '{symptom_display}'. Please monitor your condition and consult a physician.",
                        'doctor_text': f"Chief Complaint: {symptom_display}\n\nGuidelines Found:\n{retrieved_docs if retrieved_docs else 'None'}\n\nPlan: Standard evaluation."
                    }

with col2:
    if 'result' in st.session_state:
        res = st.session_state['result']
        
        if not res['is_safe']:
            st.markdown(f'<div class="alert-box">CRITICAL ALERT: {res["alert"]}</div>', unsafe_allow_html=True)
        else:
            st.success("Safety Check: Passed")
            
        st.markdown(f"""
        <div class="output-box">
            <strong>Patient Guidance</strong><br><br>
            {res['patient_text']}
        </div>
        """, unsafe_allow_html=True)
        
        doctor_html = res['doctor_text'].replace('\n', '<br>')
        st.markdown(f"""
        <div class="output-box">
            <strong>Physician Summary</strong><br><br>
            {doctor_html}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Sign & Approve"):
            st.success("Approved by physician.")
    else:
        st.write("Awaiting input...")
