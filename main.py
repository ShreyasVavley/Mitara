from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any

from context_engine import ContextEngine, PatientContext
from rag_store import RAGStore
from safety_engine import SafetyEngine

app = FastAPI(title="Mitara AI API", description="Clinical decision-support infrastructure.")

context_engine = ContextEngine()
rag_store = RAGStore()
safety_engine = SafetyEngine()

class PatientInput(BaseModel):
    symptoms_text: str
    history_text: str = ""
    meds_text: str = ""
    transcript: str = ""

class BifurcatedOutput(BaseModel):
    safety_flag: bool
    safety_message: str
    patient_guidance: str
    doctor_brief: str
    requires_doctor_verification: bool = True

@app.post("/analyze", response_model=BifurcatedOutput)
async def analyze_patient(patient_input: PatientInput):
    # 1. Safety Interception
    combined_text = f"{patient_input.symptoms_text} {patient_input.history_text} {patient_input.meds_text} {patient_input.transcript}"
    is_emergency, safety_message = safety_engine.evaluate_input(combined_text)
    
    if is_emergency:
        return BifurcatedOutput(
            safety_flag=True,
            safety_message=safety_message,
            patient_guidance="Please seek emergency medical attention immediately.",
            doctor_brief="URGENT: Patient reports critical symptoms indicative of a medical emergency.",
            requires_doctor_verification=True
        )

    # 2. Context Extraction
    context = context_engine.process_input(
        patient_input.symptoms_text,
        patient_input.history_text,
        patient_input.meds_text,
        patient_input.transcript
    )

    # 3. RAG Retrieval
    query = " ".join([s.description for s in context.symptoms])
    guidelines = rag_store.get_grounded_context(query)

    # 4. LLM Generation via official Ollama Python client
    # using Llama 3 with low temperature for strict grounding.
    import ollama
    import json
    
    system_prompt = "You are a clinical AI. Output MUST be in valid JSON format with exactly two keys: 'patient_guidance' (plain language, calibrated to literacy) and 'doctor_brief' (structured, professional clinical brief)."
    prompt = f"Patient presents with: {query}.\nMedical History: {', '.join(context.history.conditions)}.\nCurrent Meds: {', '.join(context.medications.current_medications)}.\nClinical Guidelines Retrieved:\n{guidelines}\n\nGenerate the guidance and brief based ONLY on these guidelines."
    
    try:
        response = ollama.chat(model='llama3', messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': prompt}
        ], format='json', options={'temperature': 0.1})
        
        llm_output = json.loads(response['message']['content'])
        patient_guidance = llm_output.get('patient_guidance', 'Error generating guidance.')
        doctor_brief = llm_output.get('doctor_brief', 'Error generating brief.')
    except Exception as e:
        # Smarter dynamic fallback for offline demo purposes
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

    # 5. Output Validation
    if not safety_engine.validate_output(patient_guidance):
        raise HTTPException(status_code=500, detail="Generated output failed safety validation.")

    return BifurcatedOutput(
        safety_flag=False,
        safety_message="Safe",
        patient_guidance=patient_guidance,
        doctor_brief=doctor_brief,
        requires_doctor_verification=True
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
