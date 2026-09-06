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
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.red_flag_patterns]

    def evaluate_input(self, text: str) -> Tuple[bool, str]:
        """
        Evaluates input text for emergency keywords.
        Returns a tuple: (is_emergency, message)
        """
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
