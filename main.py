# app.py
import os
from pathlib import Path
from flask import Flask, request, jsonify
from pdf2image import convert_from_path
from werkzeug.utils import secure_filename

from core import ocr, vision, llm

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/process', methods=['POST'])
def process_blueprint():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(pdf_path)

        try:
            images = convert_from_path(pdf_path, dpi=150)
            
            rulebook = ocr.extract_rulebook_from_images(images)
            
            raw_detections = vision.detect_emergency_lights_with_vlm(images)
            if not raw_detections:
                return jsonify({"error": "No light fixtures were detected by the vision model."}), 404

            final_summary = llm.group_and_summarize_detections(raw_detections, rulebook)

            return jsonify(final_summary)

        except Exception as e:
            return jsonify({"error": "An error occurred during processing", "details": str(e)}), 500
        
        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
    
    return jsonify({"error": "Invalid file type, please upload a PDF."}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)