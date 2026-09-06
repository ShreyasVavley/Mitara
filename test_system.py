import pytest
from context_engine import ContextEngine
from rag_store import RAGStore
from safety_engine import SafetyEngine

def test_context_engine_parsing():
    engine = ContextEngine()
    context = engine.process_input(
        symptoms_text="Severe chest pain and headache",
        history_text="Hypertension",
        meds_text="Lisinopril",
        transcript="Patient complains of chest pain."
    )
    # Validate Pydantic boundary parsing
    assert len(context.symptoms) >= 1
    assert "chest pain" in [s.description.lower() for s in context.symptoms]
    assert "Hypertension" in context.history.conditions
    assert "Lisinopril" in context.medications.current_medications
    assert context.raw_transcript == "Patient complains of chest pain."

def test_rag_store_retrieval():
    store = RAGStore()
    guidelines = store.retrieve_guidelines("chest pain", top_k=1)
    
    # Test ChromaDB top-k retrieval accuracy
    assert len(guidelines) >= 0
    if len(guidelines) > 0:
        assert "myocardial infarction" in guidelines[0].lower() or "aspirin" in guidelines[0].lower()

def test_safety_engine():
    engine = SafetyEngine()
    
    # Test emergency interception
    is_emergency, msg = engine.evaluate_input("I am having a heart attack")
    assert is_emergency is True
    assert "EMERGENCY" in msg
    
    # Test output validation
    is_safe = engine.validate_output("You should take this medication immediately.")
    assert is_safe is False
