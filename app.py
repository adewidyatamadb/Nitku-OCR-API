import pytesseract
from pdf2image import convert_from_path
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import re
import os
import threading

# Configure Tesseract and Poppler paths
# Get the root directory dynamically
root_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the paths relative to the root directory
tesseract_cmd = os.path.join(root_dir, 'Tesseract-OCR', 'tesseract.exe')
poppler_path = os.path.join(root_dir, 'poppler-24.07.0', 'Library', 'bin')

# Assign the paths
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
poppler_path = poppler_path

# Initialize Flask app and API
app = Flask(__name__)
api = Api(app)

class OCR(Resource):
    def post(self):
        if 'file' not in request.files:
            return {"message": "No file part"}, 400
        file = request.files['file']
        if file.filename == '':
            return {"message": "No selected file"}, 400
        if file:
            upload_dir = 'D:/Portal/Nitku/uploads'
            file_path = os.path.join(upload_dir, file.filename)

            # Create the directory if it doesn't exist
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            file.save(file_path)
            nitku_dict = process_pdf(file_path)
            return nitku_dict, 200

def process_pdf(pdf_path):
    pages = convert_from_path(pdf_path, poppler_path=poppler_path)
    ocr_results = {}
    for i, page in enumerate(pages):
        text = pytesseract.image_to_string(page)
        ocr_results[f'Page_{i+1}'] = text

    # Combine all text from all pages
    combined_text = " ".join(ocr_results.values())

    # Regular expression to find NITKU values
    nitku_pattern = re.compile(f'NITKU\s*[:;]\s*(\d+)')
    nitku_values = nitku_pattern.findall(combined_text)

    # Store NITKU values in a dictionary
    nitku_dict = {
        'nitku_penjual': nitku_values[0] if len(nitku_values) > 0 else None,
        'nitku_lawan_transaksi': nitku_values[1] if len(nitku_values) > 1 else None
    }

    return nitku_dict

api.add_resource(OCR, '/ocr')

# Function to run Flask app in a separate thread
def run_app():
    app.run(debug=False, port=130, use_reloader=False)

# Start Flask app
thread = threading.Thread(target=run_app)
thread.start()