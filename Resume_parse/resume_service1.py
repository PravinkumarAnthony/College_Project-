from flask import Flask, request, jsonify, render_template
import os
import docx
import PyPDF2
import requests
import json

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

supported_formats = ['.docx', '.pdf']

groq_api_key = "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"
groq_endpoint = "https://api.groq.com/openai/v1/chat/completions"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_file(file):
    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    text = ''
    
    if filename.endswith('.docx'):
        doc = docx.Document(file_path)
        text = '\n'.join([para.text for para in doc.paragraphs])
    elif filename.endswith('.pdf'):
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() or ''
    
    return text

def parse_resume_with_groq(text):
    prompt = f"""
   Enhanced Prompt:

Extract the following details from the given resume text:

Name

Email

Phone Number

Skills

Years of Experience

  Resume Text:
    {text}
    
    Return only the extracted details in JSON format. Do not include any reasoning, step-by-step thought process, or intermediate calculations in the output
  .
    """
    
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-r1-distill-llama-70b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }
    
    try:
        response = requests.post(groq_endpoint, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an error for HTTP errors
        return response.json()  # Return the full JSON response
    except requests.exceptions.RequestException as e:
        print(f"Error calling Groq API: {e}")
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and any(file.filename.endswith(ext) for ext in supported_formats):
        extracted_text = extract_text_from_file(file)
        result = parse_resume_with_groq(extracted_text)
        
        # Directly return the result as JSON
        return jsonify(result), 200
    
    return jsonify({'error': 'File type not supported'}), 400

if __name__ == '__main__':
    app.run(debug=True)