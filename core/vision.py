# core/vision.py
import google.generativeai as genai
import json
from PIL import Image
from typing import List
from .config import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)
vlm_model = genai.GenerativeModel('gemini-pro-vision')

def detect_emergency_lights_with_vlm(images: List[Image.Image]) -> List[dict]:
    all_detections = []
    
    prompt = """
    You are an expert electrical engineer assistant. Analyze this blueprint image.
    Your task is to identify ALL emergency lighting fixtures, which are typically fully shaded rectangular boxes.
    For each fixture you find, identify its symbol (e.g., "A1E", "W", "F3") located next to it.
    
    Return the output as a valid JSON array of objects. Each object must have one key: "symbol".
    Example output format:
    [
        {"symbol": "A1E"},
        {"symbol": "A1E"},
        {"symbol": "W"}
    ]

    If you find no emergency lights, return an empty array [].
    Do NOT add any other text, explanations, or markdown formatting like ```json outside of the final JSON array.
    """

    for i, img in enumerate(images):
        try:
            response = vlm_model.generate_content([prompt, img], stream=False)
            response_text = response.text.strip().replace("```json", "").replace("```", "")
            page_detections = json.loads(response_text)
            
            for detection in page_detections:
                detection["source_sheet"] = f"Page {i+1}"
            all_detections.extend(page_detections)
        except Exception:
            continue
            
    return all_detections