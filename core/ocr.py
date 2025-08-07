# core/ocr.py
from transformers import VisionEncoderDecoderModel, NougatImageProcessor, NougatTokenizer
from PIL import Image
from typing import List
import re
import torch

model_name = "facebook/nougat-small"
image_processor = NougatImageProcessor.from_pretrained(model_name)
tokenizer = NougatTokenizer.from_pretrained(model_name)
model = VisionEncoderDecoderModel.from_pretrained(model_name)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

def extract_rulebook_from_images(images: List[Image.Image]) -> dict:
    rulebook = {"notes": [], "schedule": []}
    
    for image in images:
        if not image.mode == "RGB":
            image = image.convert("RGB")

        pixel_values = image_processor(image, return_tensors="pt").pixel_values
        
        outputs = model.generate(
            pixel_values.to(device),
            min_length=1,
            max_length=4096,
            bad_words_ids=[[tokenizer.unk_token_id]],
        )
        
        generated_sequence = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        
        if re.search(r'lighting schedule', generated_sequence, re.IGNORECASE):
            table_lines = generated_sequence.split('\n')
            header_found = False
            for line in table_lines:
                if 'Symbol' in line and 'Description' in line:
                    header_found = True
                    continue
                if header_found and '|' in line:
                    parts = [p.strip() for p in line.split('|') if p.strip()]
                    if len(parts) >= 2:
                        rulebook["schedule"].append({
                            "symbol": parts[0],
                            "description": parts[1],
                            "raw_data": ' | '.join(parts)
                        })

        if re.search(r'general notes', generated_sequence, re.IGNORECASE):
            notes_section = re.split(r'general notes', generated_sequence, flags=re.IGNORECASE)[-1]
            notes = re.findall(r'^\s*[\d\.\-•]\s*(.*)', notes_section, re.MULTILINE)
            rulebook["notes"].extend([note.strip() for note in notes])
            
    return rulebook