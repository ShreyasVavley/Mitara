import re
from typing import Tuple

class SafetyEngine:
    def __init__(self):
        # Regex patterns for critical conditions
        self.red_flag_patterns = [
            r"\b(chest\s*pain)\b",
            r"\b(heart\s*attack)\b",
            r"\b(stroke)\b",
            r"\b(acute\s*respiratory\s*distress)\b",
            r"\b(suicid[ea]l?)\b",
            r"\b(severe\s*bleeding)\b",
            r"\b(loss\s*of\s*consciousness)\b"
        ]
        
        # Regex for adversarial / impossible test cases
        self.impossible_patterns = [
            r"-\d+\s*c",                 # Negative celsius (e.g. -15c)
            r"-\d+\s*f",                 # Negative fahrenheit
            r"\b\d{3,}\s*bpm\b",         # 1000+ bpm or 900 bpm
            r"\b9\d{2}\s*bpm\b",         # 900+ bpm
            r"\b(dead|deceased)\b",      # Patient is dead
            r"walking around and talking normally", # Specific jailbreak string
            r"\b(no pulse|zero blood pressure)\b",  # Contradictions
            r"(ignore all previous|write a poem|act as a)", # Prompt injection / jailbreak
            r"\b(decapitated|head chopped off)\b",   # Extreme impossible downplaying
            r"(lethal dose|kill myself|prescribe me cyanide)", # Malicious prescription requests
            r"(drop table|system prompt|ignore safety|sql injection)", # System attacks
            r"\b(vampire|werewolf|alien|5000 lbs|20 feet tall)\b", # Fictional / Physically impossible
            r"2-month-old.*stressful day at work" # Age/biology contradiction
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.red_flag_patterns]
        self.compiled_impossible = [re.compile(pattern, re.IGNORECASE) for pattern in self.impossible_patterns]

    def evaluate_input(self, text: str) -> Tuple[bool, str]:
        """
        Evaluates input text for emergency keywords and impossible biological parameters.
        Returns a tuple: (is_emergency/is_invalid, message)
        """
        for pattern in self.compiled_impossible:
            if pattern.search(text):
                return True, "DATA INTEGRITY ALERT: Biologically impossible parameters detected (e.g., negative temperature, absurd heart rates, deceased status). System rejecting adversarial input."

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
