from pydantic import BaseModel, Field
from typing import List, Optional

class SymptomInfo(BaseModel):
    description: str
    duration: Optional[str] = None
    severity: Optional[str] = None

class MedicalHistoryInfo(BaseModel):
    conditions: List[str] = Field(default_factory=list)
    surgeries: List[str] = Field(default_factory=list)
    family_history: List[str] = Field(default_factory=list)

class MedicationInfo(BaseModel):
    current_medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)

class PatientContext(BaseModel):
    symptoms: List[SymptomInfo] = Field(default_factory=list)
    history: MedicalHistoryInfo = Field(default_factory=MedicalHistoryInfo)
    medications: MedicationInfo = Field(default_factory=MedicationInfo)
    raw_transcript: Optional[str] = None

class ContextEngine:
    def parse_symptoms(self, text: str) -> List[SymptomInfo]:
        # In a real scenario, this would use NLP or an LLM to extract symptoms
        if "chest pain" in text.lower():
            return [SymptomInfo(description="Chest pain", severity="Severe")]
        return [SymptomInfo(description=text)]

    def parse_history(self, text: str) -> MedicalHistoryInfo:
        # Dummy parser
        return MedicalHistoryInfo(conditions=[text] if text else [])

    def parse_medications(self, text: str) -> MedicationInfo:
        # Dummy parser
        return MedicationInfo(current_medications=[text] if text else [])

    def process_input(self, symptoms_text: str, history_text: str, meds_text: str, transcript: str = None) -> PatientContext:
        """
        Processes streams separately and merges into a unified context.
        """
        symptoms = self.parse_symptoms(symptoms_text)
        history = self.parse_history(history_text)
        medications = self.parse_medications(meds_text)
        
        return PatientContext(
            symptoms=symptoms,
            history=history,
            medications=medications,
            raw_transcript=transcript
        )
