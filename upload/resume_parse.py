from flask import Flask, request, jsonify, render_template
import os
import re
import docx
import PyPDF2

app = Flask(__name__)

# Define the folder path where the resumes are stored temporarily for processing
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Supported file types (docx, pdf)
supported_formats = ['.docx', '.pdf']

required_skills = {'.net', 'java', 'llm', 'python', 'c#'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to extract contact information (email and phone number)
def extract_contact_info(text):
    email_regex = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    email = re.search(email_regex, text)

    phone_regex = r"\+?\d{1,3}?[-.\s]?\(?\d{1,4}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}"
    phone = re.search(phone_regex, text)

    return (email.group(0) if email else "No email found", phone.group(0) if phone else "No phone number found")

# Function to extract skills from resume text
def extract_skills(text):
    skills_list = ['.net', 'java', 'llm', 'python', 'c++', 'javascript', 'html', 'css', 'sql', 'aws', 'c#']
    found_skills = {skill for skill in skills_list if skill.lower() in text.lower()}
    return found_skills

# Function to extract years of experience
def extract_experience(text):
    experience_regex = r"(\d+)\+?\s?(years?|yrs?)\s?(of\s)?experience"
    match = re.search(experience_regex, text.lower())
    return int(match.group(1)) if match else 0

# Function to calculate score based on matched skills and experience
def calculate_score(found_skills, required_skills, experience):
    matched_skills = required_skills & found_skills
    unmatched_skills = required_skills - found_skills

    score = 0
    score += len(matched_skills) * 10  # 10 points for each matched skill
    score -= len(unmatched_skills) * 5  # Deduct 5 points for each unmatched skill
    score += experience * 2  # 2 points for each year of experience

    return score, matched_skills, unmatched_skills

# Function to process uploaded resume file
def process_resume(file):
    # Save the file temporarily
    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    text = ''
    
    # Process DOCX file
    if filename.endswith('.docx'):
        doc = docx.Document(file_path)
        text = '\n'.join([para.text for para in doc.paragraphs])

    # Process PDF file
    elif filename.endswith('.pdf'):
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text()

    # Extract skills, contact info, and experience
    found_skills = extract_skills(text)
    email, phone = extract_contact_info(text)
    experience = extract_experience(text)

    # Calculate score
    score, matched_skills, unmatched_skills = calculate_score(found_skills, required_skills, experience)

    # Determine selection status
    status = "selected" if score > 50 else "not selected"

    result = {
        'filename': filename,
        'skills_found': list(found_skills),
        'required_skills': list(required_skills),
        'matched_skills': list(matched_skills),
        'unmatched_skills': list(unmatched_skills),
        'email': email,
        'phone': phone,
        'experience': experience,
        'score': score,
        'status': status
    }

    return result

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
        result = process_resume(file)
        return jsonify(result), 200

    return jsonify({'error': 'File type not supported'}), 400

if __name__ == '__main__':
    app.run(debug=True)
