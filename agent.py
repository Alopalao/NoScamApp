import os
import json
import time
from typing import Dict, Any, List
from settings import MY_KEY

# To run this script, you will need to install the google-genai library:
# pip install google-genai

from google import genai
from google.genai import types
from google.genai.errors import APIError

# --- Configuration ---
# IMPORTANT: Replace 'YOUR_API_KEY' with your actual Gemini API key.
# It is best practice to set this as an environment variable (GEMINI_API_KEY)
# and load it like below.
API_KEY = MY_KEY
MODEL_NAME = "gemini-2.5-flash"
MAX_RETRIES = 5

class Agent:
    def __init__(self):
        self.client = genai.Client(api_key=API_KEY)

    def get_analysis(self, email):
        scam_email = (
            "URGENT ACTION REQUIRED! Your Medicare Benefit Account has been flagged for suspension. "
            "You must immediately click the link below to verify your password and date of birth "
            "within the next 30 minutes or all future health coverage will be permanently revoked. "
            "Click here: https://medicare-verify.xyz/update"
        )
        
        print(f"INPUT: \n'{email}...'\n")
        
        scam_result = self.detect_scam(self.client, email)

        print(json.dumps(scam_result, indent=4))
        return scam_result

    def get_scam_detection_system_instruction(self) -> str:
        """
        Defines the role and rules for the Gemini model to perform scam detection.
        This instruction guides the model to act as a highly specialized analyst.
        """
        return (
            "You are a highly specialized Fraud and Scam Detection Analyst. "
            "Your task is to analyze incoming email or message text and determine "
            "if it is a SCAM or LEGITIMATE, specifically targeting vulnerable populations "
            "(seniors, those with health or financial concerns) to steal credentials or money. "

            "Follow these rules strictly:\n"
            "1. **Analyze:** Carefully review the tone, urgency, sender legitimacy, "
            "and request type (banking, insurance, health). "
            "2. **Criteria for SCAM:** An email is a SCAM if it exhibits high-risk indicators such as:\n"
            "    - **Urgency/Threats:** Immediate action required (e.g., 'Account suspended in 2 hours'), "
            "      threats of legal action, fines, or loss of benefits/health coverage.\n"
            "    - **Credential Requests:** Requests to 'verify' passwords, PINs, or account numbers via a link or reply.\n"
            "    - **False Authority:** Claims to be from major banks, insurance companies (like Medicare/Medicaid), "
            "      or government agencies with unusual communication methods or requests.\n"
            "    - **Suspicious Links:** Prompts to click links to 'cancel a transaction' or 'claim a prize'.\n"
            "3. **Criteria for LEGITIMATE:** An email is LEGITIMATE if it is routine, informational, "
            "   lacks high-pressure tactics, and directs the user to established, secure channels (e.g., 'Log in through our official website').\n"
            "4. **Output Format:** You MUST respond with a single JSON object. Do not include any text, preamble, or markdown formatting outside of the JSON object."
            "5. Verify the names of the companies in the emails. I have seem some generic names like Endurance bank, PlushHealth insurance, MoreMoney credit or others."
        )

    def create_json_schema(self) -> types.Schema:
        """
        Defines the strict JSON output structure for the classification result.
        This forces the model to return a reliable, parsable result with concise reasoning.
        """
        # Define reasoning properties as a dictionary for cleaner iteration
        reasoning_properties = {
            "urgency": types.Schema(
                type=types.Type.STRING,
                description="Analysis of urgency tactics in 1-2 sentences (max 100 characters). Describe time pressure or threats briefly. If none, state 'No urgency detected.'"
            ),
            "tone": types.Schema(
                type=types.Type.STRING,
                description="Analysis of tone in 1-2 sentences (max 100 characters). Mention if threatening, unprofessional, or has errors. Keep it brief."
            ),
            "sender_legitimacy": types.Schema(
                type=types.Type.STRING,
                description="Analysis of sender credibility in 1-2 sentences (max 100 characters). Note if sender seems legitimate or suspicious by veryfying that the company actually exists and is related to any address given. Be concise."
            ),
            "requests": types.Schema(
                type=types.Type.STRING,
                description="What the message requests in 1-2 sentences (max 100 characters). Mention credentials, money, or link clicks. If none, state 'No suspicious requests.'"
            ),
            "red_flags": types.Schema(
                type=types.Type.STRING,
                description="Key red flags in 1-2 sentences (max 120 characters). List 2-3 most critical warning signs only. Be specific but brief."
            )
        }
    
        # Build the reasoning schema
        reasoning_schema = types.Schema(
            type=types.Type.OBJECT,
            properties=reasoning_properties,
            description="Detailed breakdown of reasoning across multiple analysis dimensions. Keep each field concise for UI display."
        )
    
        # Define main properties
        main_properties = {
            "classification": types.Schema(
                type=types.Type.STRING,
                description="The final verdict: either 'SCAM' or 'LEGITIMATE'."
            ),
            "reasoning": reasoning_schema,
            "risk_score": types.Schema(
                type=types.Type.INTEGER,
                description="A score from 1 (Very Low Risk) to 10 (Critical Risk) indicating the severity of the threat."
            )
        }
    
        # Return the complete schema
        return types.Schema(
            type=types.Type.OBJECT,
            properties=main_properties,
            required=list(main_properties.keys())
        )

    def detect_scam(self, client: genai.Client, email_text: str) -> Dict[str, Any]:
        """
        Calls the Gemini API to classify the email text with retry logic.

        Args:
            client: The configured Gemini API client.
            email_text: The text content of the email to analyze.

        Returns:
            A dictionary containing the classification result or an error message.
        """
        system_instruction = self.get_scam_detection_system_instruction()
        json_schema = self.create_json_schema()

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=json_schema
        )

        for attempt in range(MAX_RETRIES):
            try:
                print(f"-> Analyzing (Attempt {attempt + 1}/{MAX_RETRIES})...")
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[email_text],
                    config=config,
                )

                # The response text should be a valid JSON string due to the configuration
                result = json.loads(response.text.strip())
                return result

            except APIError as e:
                # Handle API errors (e.g., rate limiting, authorization issues)
                print(f"API Error on attempt {attempt + 1}: {e}")
                if attempt < MAX_RETRIES - 1:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    return {"error": "API Error: Max retries reached."}

            except json.JSONDecodeError:
                # Handle cases where the model fails to return valid JSON
                print(f"JSON Decode Error on attempt {attempt + 1}. Raw output: {response.text.strip()}")
                if attempt < MAX_RETRIES - 1:
                    print("Retrying with same prompt...")
                else:
                    return {"error": "Model failed to produce valid JSON output."}

            except Exception as e:
                # Catch all other exceptions
                return {"error": f"An unexpected error occurred: {e}"}

# --- Example Usage ---

#if __name__ == "__main__":
#    try:
#        # Initialize the client
#        print(f"Gemini Client initialized. Using model: {MODEL_NAME}")
#        
#        # --- Test Case 1: High-Risk Phishing Scam (Urgency + Credential Request) ---
#        
#        print("\n" + "="*50)
#        print("TEST CASE 1: Medicare Phishing Scam")
#        print("="*50)
#        print("\n--- CLASSIFICATION RESULT ---")
#        
#        
#        # --- Test Case 2: Legitimate (Routine, No Urgency/Credential Request) ---
#        legit_email = (
#            "Dear Customer, we're writing to let you know about an upcoming scheduled maintenance for our "
#            "online banking portal. You may experience brief outages between 2:00 AM and 4:00 AM EST on Saturday. "
#            "Your account security is our top priority. Please log in through our official website after the maintenance window to check your balances. "
#            "Do not click any links from unauthorized sources. This is purely informational."
#        )
#        print("\n" + "="*50)
#        print("TEST CASE 2: Routine Banking Update (Legitimate)")
#        print("="*50)
#        print(f"INPUT: \n'{legit_email[:120]}...'\n")
#        legit_result = detect_scam(client, legit_email)
#        print("\n--- CLASSIFICATION RESULT ---")
#        print(json.dumps(legit_result, indent=4))
#    except Exception as e:
#        print(f"\nFATAL ERROR during script execution: {e}")
