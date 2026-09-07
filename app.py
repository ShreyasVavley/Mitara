import streamlit as st
import time
from context_engine import ContextEngine
from safety_engine import SafetyEngine
from rag_store import RAGStore

@st.cache_resource
def load_systems():
    return ContextEngine(), SafetyEngine(), RAGStore(data_directory="medical_data")

ctx_engine, safety, rag = load_systems()

st.set_page_config(page_title="Mitara AI", layout="wide")

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
    <h1 style="margin:0; font-size: 28px;">Mitara AI</h1>
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
