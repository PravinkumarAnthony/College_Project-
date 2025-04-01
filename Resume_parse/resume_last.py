import re
import fitz  # PyMuPDF
import docx
import spacy
from tabulate import tabulate # type: ignore

# Load the spaCy model for Named Entity Recognition
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text("text") for page in doc)
    return text

def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file."""
    doc = docx.Document(docx_path)
    text = "\n".join(para.text for para in doc.paragraphs)
    return text

def extract_email(text):
    """Extract email addresses from text using regex."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else None

def extract_mobile(text):
    """
    Extract a mobile number using a regex that captures a wide variety of formats.
    This pattern matches numbers with country codes, spaces, dashes, and parentheses.
    """
    mobile_pattern = r'\+?\d[\d\-\(\) ]{7,}\d'
    mobiles = re.findall(mobile_pattern, text)
    return mobiles[0].strip() if mobiles else None

def extract_section_full(text, section_keyword):
    """
    Extract the full content of a section given a section header keyword.
    The function captures everything after the section header until the next section header
    (a line starting with a capital letter and ending with a colon or dash) or end-of-text.
    """
    pattern = re.compile(
        r'(?i)' + re.escape(section_keyword) + r'\s*[:\-]?\s*(.*?)(?=\n[A-Z][A-Za-z0-9 ]{1,}[:\-]|$)',
        re.DOTALL
    )
    match = pattern.search(text)
    if match:
        section_text = match.group(1).strip()
        return section_text
    return None

def extract_name(text, email, mobile):
    """
    Extract the candidate's name by combining spaCy's NER with fallback heuristics.
    
    First, attempt to use spaCy's NER to identify entities labeled as PERSON with at least two words.
    If no valid candidate is found, scan through the text lines for a likely name candidate that:
      - Does not include the email or mobile.
      - Contains at least two words.
      - Has a reasonable length and doesn't include digits or header keywords.
    """
    # First try using spaCy's NER
    doc = nlp(text)
    candidate_names = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON" and len(ent.text.split()) >= 2]
    if candidate_names:
        return candidate_names[0]

    # Fallback heuristic: iterate through lines
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if email and email in line:
            continue
        if mobile and mobile in line:
            continue
        # Check if line is a potential name candidate
        if len(line.split()) >= 2 and len(line) < 40:
            # Exclude lines that contain digits or common resume keywords
            if not re.search(r'\d', line) and not re.search(r'Email|Mobile|Skills|Experience', line, re.I):
                return line
    return None

def parse_resume(file_path):
    """Parse resume and extract details."""
    if file_path.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide a PDF or DOCX file.")

    email = extract_email(text)
    mobile = extract_mobile(text)
    name = extract_name(text, email, mobile)
    
    # Extract full sections for skills and experience.
    skills = extract_section_full(text, "Skills")
    experience = extract_section_full(text, "Experience")
    if not experience:
        experience = extract_section_full(text, "Work Experience")
    
    return {
        "Name": name if name else "Not Found",
        "Email": email if email else "Not Found",
        "Mobile": mobile if mobile else "Not Found",
        "Skill Sets": skills if skills else "Not Found",
        "Experience": experience if experience else "Not Found"
    }

def display_table(data):
    """Display extracted details in a table."""
    headers = ["Field", "Value"]
    table_data = [[field, data.get(field, "Not Found")] for field in ["Name", "Email", "Mobile", "Skill Sets", "Experience"]]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

# Example usage:
if __name__ == "__main__":
    file_path = "sample_resume.pdf"  # Update with your resume file (PDF or DOCX)
    details = parse_resume(file_path)
    display_table(details)
