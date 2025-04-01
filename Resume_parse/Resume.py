import re
import fitz  # type: ignore # PyMuPDF
import docx # type: ignore

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])
    return text

def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file."""
    doc = docx.Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def extract_email(text):
    """Extract email address from text using regex."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails if emails else None

def parse_resume(file_path):
    """Parse resume and extract email."""
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide a PDF or DOCX file.")
    
    return extract_email(text)

# Example usage
if __name__ == "__main__":
    file_path = "Pravin Resume.pdf"  # Change to your file name
    emails = parse_resume(file_path)
    print("Extracted Email(s):", emails)
