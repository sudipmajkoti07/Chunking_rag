from PyPDF2 import PdfReader

def extract_text_from_file(file):
    if file.filename.endswith(".pdf"):
        reader = PdfReader(file.file)
        text = "".join([page.extract_text() or "" for page in reader.pages])
    elif file.filename.endswith(".txt"):
        text = file.file.read().decode("utf-8")
    else:
        raise ValueError("Unsupported file type")
    return text.strip()
