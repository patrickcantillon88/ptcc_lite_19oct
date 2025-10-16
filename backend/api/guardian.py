#!/usr/bin/env python3
"""
Project Guardian API for PTCC

Digital citizenship breach triage system using Google's Gemini AI.
Classifies incidents into LOW, MEDIUM, or HIGH severity levels.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal
import os
import json

from ..core.logging_config import get_logger

logger = get_logger("api.guardian")
router = APIRouter()

# Gemini AI client (lazy loaded)
_genai_client = None


def get_gemini_client():
    """Get or initialize Gemini AI client"""
    global _genai_client
    if _genai_client is None:
        try:
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
            genai.configure(api_key=api_key)
            _genai_client = genai
            logger.info("Gemini AI client initialized successfully")
        except ImportError:
            logger.error("google-generativeai package not installed")
            raise HTTPException(
                status_code=500,
                detail="AI service not available. Install google-generativeai package."
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize AI service: {str(e)}"
            )
    return _genai_client


class AssessmentRequest(BaseModel):
    """Request model for incident assessment"""
    description: str
    year_group: str
    incident_history: Literal["First incident", "Repeated offense"]


class Assessment(BaseModel):
    """Response model for incident assessment"""
    classification: Literal["LOW", "MEDIUM", "HIGH"]
    reason: str
    next_steps: List[str]


SYSTEM_INSTRUCTION = """You are an expert AI assistant for school staff, designed to triage digital citizenship breaches. Your role is to assess an incident's severity and recommend a resolution level. Your response must be objective, professional, and based on the provided details.

You will receive the student's year group, whether this is a first-time or repeated offense, and a description of the incident.

You must classify the incident into one of three levels: LOW, MEDIUM, or HIGH.

Your response must be a JSON object containing:
1. 'classification': LOW, MEDIUM, or HIGH.
2. 'reason': A concise explanation for your classification.
3. 'next_steps': A list of concrete, actionable next steps for the staff member.

--- ASSESSMENT CRITERIA ---

Use the following criteria to make your assessment. The final classification depends on a combination of these factors.

1.  **Incident History:**
    *   A 'Repeated offense' should almost always escalate the classification by one level compared to a 'First incident'. For example, a MEDIUM-level first offense might become HIGH if it's repeated. A LOW-level repeated offense might become MEDIUM.

2.  **Year Group:**
    *   The same behavior can have different severity depending on the student's age. This app is for primary school students (Years 3-6). A significant degree of leniency should be applied, especially for younger students in this range (Years 3-4), as they are still learning foundational digital citizenship skills. However, any form of intentional harm, bullying, or exposure to clearly inappropriate content must be treated as a serious issue, regardless of age.

3.  **Incident Type Keywords & Severity:**

    **🟢 LOW (Teacher Level Resolution):**
    *   **Characteristics:** Minor, unintentional, first-time offenses with limited impact. No clear malicious intent.
    *   **Keywords/Examples:**
        *   Accidental sharing of non-sensitive information.
        *   Using non-compliant apps (e.g., games, social media) during class for the first time.
        *   Cleared browser history for non-sensitive searches.
        *   Mildly off-topic or silly comments in a school chat.
        *   Using a VPN for the first time without accessing harmful content.
        *   Forgetting iPad or using it outside of learning time without malice.
        *   Inappropriate but not offensive profile content (e.g., a silly meme).

    **🟡 MEDIUM (Head of Year Resolution):**
    *   **Characteristics:** Deliberate but not severe breaches, repeated minor offenses, or actions with a wider or more significant impact on others. May show a lack of judgment.
    *   **Keywords/Examples:**
        *   Minor cyberbullying (e.g., unkind messages, name-calling, creating a joke meme about someone).
        *   Sharing photos/videos of others without consent where no harm was intended but privacy was breached.
        *   Persistent use of non-compliant apps or VPNs after a warning.
        *   Inappropriate searches (e.g., for swear words, non-explicit but mature topics).
        *   Using swear words in chats.
        *   Creating fake (but not malicious) accounts.
        *   Minor hacking attempts (e.g., trying to guess a friend's password as a joke).

    **🔴 HIGH (DSL Level Resolution):**
    *   **Characteristics:** Serious, malicious, or illegal behavior. Poses a significant risk to the student or others. A clear safeguarding concern.
    *   **Keywords/Examples:**
        *   Serious, persistent, or targeted cyberbullying; harassment; threats.
        *   Sharing or searching for explicit, pornographic, violent, or illegal content.
        *   Sexting: creating, sending, or receiving indecent images of minors.
        *   Impersonating others online to cause harm or distress.
        *   Hacking into accounts with malicious intent.
        *   Discriminatory behavior (racism, homophobia, etc.).
        *   Anything indicating a potential for self-harm, radicalization, or criminal activity.
        *   Taking and sharing photos/videos to humiliate or embarrass someone (e.g., in a state of undress).

--- RESPONSE GUIDELINES ---

*   For 'next_steps', provide practical actions. For MEDIUM, suggest informing the Head of Year. For HIGH, always state that the DSL must be contacted immediately. Always include logging the incident as a step.
*   Do not use student names or any personally identifiable information in your response.
*   Your 'reason' should directly reference the incident description, history, and year group to justify the classification."""


@router.post("/assess")
async def assess_incident(request: AssessmentRequest) -> Assessment:
    """
    Assess a digital citizenship breach incident using AI.
    
    Returns:
    - classification: LOW, MEDIUM, or HIGH severity
    - reason: Explanation for the classification
    - next_steps: List of recommended actions
    """
    try:
        if not request.description.strip():
            raise HTTPException(
                status_code=400,
                detail="Incident description cannot be empty"
            )
        
        # Get Gemini client
        genai = get_gemini_client()
        
        # Create the model
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "temperature": 0.2,
                "response_mime_type": "application/json",
            }
        )
        
        # Create the prompt with system instruction embedded
        prompt = f"""{SYSTEM_INSTRUCTION}

An incident has occurred. Please provide an assessment based on the following details:
- Year Group: {request.year_group}
- Incident History: {request.incident_history}
- Description: "{request.description}"

Respond with a JSON object containing: classification (LOW/MEDIUM/HIGH), reason (string), and next_steps (array of strings).
"""
        
        logger.info(f"Assessing incident for {request.year_group}, {request.incident_history}")
        
        # Generate content
        response = model.generate_content(prompt)
        
        if not response.text:
            raise HTTPException(
                status_code=500,
                detail="Received empty response from AI service"
            )
        
        # Parse JSON response
        try:
            result = json.loads(response.text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Raw response: {response.text}")
            raise HTTPException(
                status_code=500,
                detail="AI service returned invalid response format"
            )
        
        # Validate and create assessment
        assessment = Assessment(
            classification=result.get("classification", "MEDIUM"),
            reason=result.get("reason", "Unable to determine specific reason"),
            next_steps=result.get("next_steps", ["Log the incident", "Consult with supervisor"])
        )
        
        logger.info(f"Assessment complete: {assessment.classification}")
        return assessment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during incident assessment: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to assess incident: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Check if Guardian API and Gemini service are available"""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {
                "status": "degraded",
                "gemini_configured": False,
                "message": "GEMINI_API_KEY not configured"
            }
        
        # Try to initialize client
        get_gemini_client()
        
        return {
            "status": "healthy",
            "gemini_configured": True,
            "message": "Guardian API is operational"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "gemini_configured": False,
            "error": str(e)
        }
