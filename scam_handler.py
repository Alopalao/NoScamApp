from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum




class RiskLevel(Enum):
    """Enum for risk level categories based on risk score"""
    VERY_LOW = "Very Low"
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"




class ClassificationType(Enum):
    """Enum for classification types"""
    SCAM = "SCAM"
    LEGITIMATE = "LEGITIMATE"
    ERROR = "ERROR"




@dataclass
class ScamAnalysisResult:
    """
    Data class to hold formatted scam analysis results for UI display.
    """
    classification: str
    reasoning: str
    risk_score: int
    risk_level: str
    color_code: str
    icon: str
    user_friendly_message: str
    recommendations: list
    error_message: Optional[str] = None
   
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary for easy serialization"""
        return {
            "classification": self.classification,
            "reasoning": self.reasoning,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "color_code": self.color_code,
            "icon": self.icon,
            "user_friendly_message": self.user_friendly_message,
            "recommendations": self.recommendations,
            "error_message": self.error_message
        }

class ScamAnalysisUIHandler:
    """
    Handler class to process scam detection results and format them for UI display.
    """
   
    @staticmethod
    def get_risk_level(risk_score: int) -> RiskLevel:
        """
        Convert numerical risk score to a categorical risk level.
       
        Args:
            risk_score: Integer from 1-10
           
        Returns:
            RiskLevel enum value
        """
        if risk_score <= 2:
            return RiskLevel.VERY_LOW
        elif risk_score <= 4:
            return RiskLevel.LOW
        elif risk_score <= 6:
            return RiskLevel.MODERATE
        elif risk_score <= 8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
   
    @staticmethod
    def get_color_code(risk_level: RiskLevel) -> str:
        """
        Get color code for UI display based on risk level.
       
        Returns:
            Hex color code string
        """
        color_map = {
            RiskLevel.VERY_LOW: "#22C55E",    # Green
            RiskLevel.LOW: "#84CC16",         # Light Green
            RiskLevel.MODERATE: "#EAB308",    # Yellow
            RiskLevel.HIGH: "#F97316",        # Orange
            RiskLevel.CRITICAL: "#EF4444"     # Red
        }
        return color_map.get(risk_level, "#6B7280")  # Gray as default
   
    @staticmethod
    def get_icon(classification: str, risk_level: RiskLevel) -> str:
        """
        Get appropriate icon/emoji for the classification.
       
        Returns:
            Icon string (emoji or icon name)
        """
        if classification == ClassificationType.SCAM.value:
            if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                return "🚨"  # Critical alert
            else:
                return "⚠️"  # Warning
        else:
            return "✅"  # Checkmark for legitimate
   
    @staticmethod
    def generate_user_message(classification: str, risk_level: RiskLevel) -> str:
        """
        Generate a user-friendly message based on classification and risk.
       
        Returns:
            User-friendly message string
        """
        if classification == ClassificationType.SCAM.value:
            messages = {
                RiskLevel.CRITICAL: "⛔ DANGER! This is very likely a scam. Do not respond or click any links.",
                RiskLevel.HIGH: "⚠️ WARNING! This message shows strong signs of being a scam.",
                RiskLevel.MODERATE: "⚠️ CAUTION: This message has some concerning elements.",
                RiskLevel.LOW: "ℹ️ Be Careful: This message has minor warning signs.",
                RiskLevel.VERY_LOW: "ℹ️ Low Risk: This appears mostly safe but stay vigilant."
            }
            return messages.get(risk_level, "Please review this message carefully.")
        else:
            return "✅ This message appears to be legitimate. However, always verify before sharing personal information."
   
    @staticmethod
    def generate_recommendations(classification: str, risk_level: RiskLevel) -> list:
        """
        Generate actionable recommendations for the user.
       
        Returns:
            List of recommendation strings
        """
        base_recommendations = [
            "Never share passwords, PINs, or account numbers via email or text",
            "Contact organizations directly using official phone numbers from their website",
            "Be suspicious of urgent requests or threats"
        ]
       
        if classification == ClassificationType.SCAM.value:
            scam_recommendations = [
                "❌ Do NOT click any links in this message",
                "❌ Do NOT reply to this message",
                "❌ Do NOT provide any personal information",
                "✅ Delete this message immediately",
                "✅ Report this to the FTC at reportfraud.ftc.gov"
            ]
           
            if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                scam_recommendations.append("✅ Consider changing your passwords if you've already interacted with this message")
           
            return scam_recommendations + base_recommendations
        else:
            legit_recommendations = [
                "✅ Still verify the sender's email address carefully",
                "✅ When in doubt, contact the organization directly using official contact info",
                "✅ Look for signs of legitimacy (proper grammar, official branding)"
            ]
            return legit_recommendations + base_recommendations
   
    @classmethod
    def process_detection_result(cls, raw_result: Dict[str, Any]) -> ScamAnalysisResult:
        """
        Main method to process raw detection result and format for UI.
       
        Args:
            raw_result: Dictionary from detect_scam() function
           
        Returns:
            ScamAnalysisResult object with all UI-ready data
        """
        # Check for errors
        if "error" in raw_result:
            return ScamAnalysisResult(
                classification=ClassificationType.ERROR.value,
                reasoning="Unable to analyze message",
                risk_score=0,
                risk_level="Unknown",
                color_code="#6B7280",
                icon="❓",
                user_friendly_message="We couldn't analyze this message. Please be cautious.",
                recommendations=["When in doubt, don't interact with suspicious messages"]
            )
       
        # Extract data from raw result
        classification = raw_result.get("classification", "UNKNOWN")
        reasoning = raw_result.get("reasoning", "No reasoning provided")
        risk_score = raw_result.get("risk_score", 5)
       
        # Ensure risk_score is within bounds
        risk_score = max(1, min(10, risk_score))
       
        # Generate UI components
        risk_level = cls.get_risk_level(risk_score)
        color_code = cls.get_color_code(risk_level)
        icon = cls.get_icon(classification, risk_level)
        user_message = cls.generate_user_message(classification, risk_level)
        recommendations = cls.generate_recommendations(classification, risk_level)
       
        

        return ScamAnalysisResult(
            classification=classification,
            reasoning=reasoning,
            risk_score=risk_score,
            risk_level=risk_level.value,
            color_code=color_code,
            icon=icon,
            user_friendly_message=user_message,
            recommendations=recommendations
        )
