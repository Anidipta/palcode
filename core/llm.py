# core/llm.py
import google.generativeai as genai
import json
from .config import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)
llm_model = genai.GenerativeModel('gemini-pro')

def group_and_summarize_detections(detections: list, rulebook: dict) -> dict:
    prompt = f"""
    You are an intelligent electrical blueprint summarizer.
    Your task is to process a list of raw emergency light detections and a "rulebook" to create a final summary.

    **Rulebook (from Lighting Schedule):**
    {json.dumps(rulebook, indent=2)}

    **Raw Detections (from Vision Model):**
    {json.dumps(detections, indent=2)}

    **Instructions:**
    1. Group the raw detections by their "symbol".
    2. For each unique symbol, count its appearances.
    3. For each unique symbol, find its corresponding "description" from the "schedule" in the rulebook.
    4. Format the final output as a single JSON object where each key is a symbol. The value for each key should be an object with "count" and "description".

    **Example Output Format:**
    {{
      "A1E": {{ "count": 12, "description": "2x4 LED Emergency Fixture" }},
      "W": {{ "count": 5, "description": "Wall-Mounted Emergency LED" }}
    }}

    Provide ONLY the final JSON object, with no additional text or markdown formatting.
    """
    
    try:
        response = llm_model.generate_content(prompt)
        response_text = response.text.strip().replace("```json", "").replace("```", "")
        final_summary = json.loads(response_text)
        return final_summary
    except Exception as e:
        return {"error": "Failed to generate valid summary JSON.", "details": str(e)}