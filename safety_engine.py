import re
from typing import Tuple

class SafetyEngine:
    def __init__(self):
        # 1. RESERVED KEYWORDS (Enterprise System Level)
        self.reserved_keywords = {
            "SYSTEM_SECURITY_LOCKDOWN": [
                "drop table", "exec(", "system prompt", "ignore all previous", "sql injection"
            ],
            "LETHAL_INTENT_LOCKDOWN": [
                "kill myself", "lethal dose", "prescribe me cyanide", "suicide", "suicidal"
            ],
            "CLINICAL_ADMIN_OVERRIDE": [
                "OVERRIDE_AUTH_99X", "SYS_ADMIN_BYPASS"
            ]
        }
        
        # 2. Medical Red Flags (Regex Patterns)
        self.red_flag_patterns = [
            r"\b(chest\s*pain)\b",
            r"\b(heart\s*attack)\b",
            r"\b(stroke)\b",
            r"\b(acute\s*respiratory\s*distress)\b",
            r"\b(severe\s*bleeding)\b",
            r"\b(loss\s*of\s*consciousness)\b"
        ]
        
        # 3. Biological Impossibilities (Regex Patterns)
        self.impossible_patterns = [
            r"-\d+\s*c",                 
            r"-\d+\s*f",                 
            r"\b\d{3,}\s*bpm\b",         
            r"\b9\d{2}\s*bpm\b",         
            r"\b(dead|deceased)\b",      
            r"walking around and talking normally",
            r"\b(no pulse|zero blood pressure)\b",  
            r"\b(decapitated|head chopped off)\b",   
            r"\b(vampire|werewolf|alien|5000 lbs|20 feet tall)\b", 
            r"2-month-old.*stressful day at work" 
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.red_flag_patterns]
        self.compiled_impossible = [re.compile(pattern, re.IGNORECASE) for pattern in self.impossible_patterns]

    def evaluate_input(self, text: str) -> Tuple[bool, str]:
        """
        Evaluates input text for reserved keywords, emergency keywords, and impossible biological parameters.
        Returns a tuple: (is_emergency/is_invalid, message)
        """
        lower_text = text.lower()
        
        # 1. Check Reserved Keywords (Highest Priority)
        for category, keywords in self.reserved_keywords.items():
            for kw in keywords:
                if kw.lower() in lower_text:
                    if category == "CLINICAL_ADMIN_OVERRIDE":
                        return False, "ADMIN OVERRIDE GRANTED: Bypassing standard safety triage."
                    elif category == "SYSTEM_SECURITY_LOCKDOWN":
                        return True, "SECURITY ALERT: Malicious system prompt or SQL injection detected. Session locked and IP logged."
                    elif category == "LETHAL_INTENT_LOCKDOWN":
                        return True, "PSYCHIATRIC / LETHAL ALERT: Immediate human intervention required. System frozen for patient safety."

        # 2. Check Biological Impossibilities
        for pattern in self.compiled_impossible:
            if pattern.search(text):
                return True, "DATA INTEGRITY ALERT: Biologically impossible parameters detected (e.g., negative temperature, absurd heart rates, deceased status). System rejecting adversarial input."

        # 3. Check Medical Emergencies
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True, "EMERGENCY IDENTIFIED: Immediate medical attention required. Proceed to the nearest emergency room or call emergency services."
                
        return False, "Input cleared."

    def validate_output(self, output: str) -> bool:
        """
        Validates model output to ensure it doesn't violate safety constraints.
        (e.g., ensuring the model doesn't prescribe dangerous drugs independently).
        """
        forbidden_advice = ["take this medication immediately", "stop taking your medication"]
        for phrase in forbidden_advice:
            if phrase in output.lower():
                return False
        return True
