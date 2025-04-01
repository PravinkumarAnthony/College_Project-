import os
import nltk
import spacy
from spacy.symbols import ORTH, NORM
from pyresparser import ResumeParser

# --- Monkey-patch spacy.load to clean tokenizer exceptions if they exist ---
original_spacy_load = spacy.load

def patched_spacy_load(name, **kwargs):
    model = original_spacy_load(name, **kwargs)
    # Only clean exceptions if the attribute exists
    if hasattr(model.tokenizer, "exceptions"):
        for key, entries in list(model.tokenizer.exceptions.items()):
            new_entries = []
            for entry in entries:
                # Only keep allowed keys: ORTH and NORM
                cleaned_entry = {k: v for k, v in entry.items() if k in {ORTH, NORM}}
                new_entries.append(cleaned_entry)
            model.tokenizer.exceptions[key] = new_entries
        print("[DEBUG] Cleaned tokenizer exceptions.")
    else:
        print("[DEBUG] Tokenizer has no 'exceptions' attribute; skipping cleaning.")
    return model

# Override spacy.load with the patched version
spacy.load = patched_spacy_load
# ---------------------------------------------------------

# Download required resources
nltk.download('stopwords')
spacy.cli.download("en_core_web_sm")

def extract_name_from_resume(resume_path):
    if not os.path.exists(resume_path):
        raise FileNotFoundError("Resume file not found. Please check the file path.")
    
    # Attempt to extract data using pyresparser
    try:
        data = ResumeParser(resume_path).get_extracted_data()
        print("[DEBUG] Extracted data:", data)
    except Exception as e:
        print("[DEBUG] Error during resume parsing:")
        raise e  # Re-raise exception after debug print
    
    if "name" in data and data["name"]:
        return data["name"]
    else:
        return "Name not found in the resume."

# Example usage
if __name__ == "__main__":
    resume_path = "sample_resume.pdf"  # Change to your actual file path
    try:
        name = extract_name_from_resume(resume_path)
        print("Extracted Name:", name)
    except Exception as err:
        print("An error occurred during processing:")
        print(err)
