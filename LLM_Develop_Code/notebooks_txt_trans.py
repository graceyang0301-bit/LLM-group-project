import pdfplumber
import os
import re
from pathlib import Path

PDF_FOLDER = "/Users/xinkewang/Desktop/U/Lingnan University/Course/Term2/CDS547_Intro to Large Language Models/group assignment/30篇计算机:社科:医学/计算机/原PDF"
OUTPUT_FOLDER = "/Users/xinkewang/Desktop/U/Lingnan University/Course/Term2/CDS547_Intro to Large Language Models/group assignment/30篇计算机:社科:医学/计算机/计科最小化清洗"
# ===================

def clean_text_minimal(text):
    if not text:
        return ""
    
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    
    return text

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

pdf_files = list(Path(PDF_FOLDER).glob("*.pdf"))
pdf_files.sort()

for i, pdf_path in enumerate(pdf_files, 1):
    print(f"process {i}/{len(pdf_files)}: {pdf_path.name}")
    
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    
    cleaned_text = clean_text_minimal(full_text)
    
    new_filename = f"cs_paper_{i:03d}.txt"
    txt_path = os.path.join(OUTPUT_FOLDER, new_filename)
    
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)
    
    print(f"  saved: {new_filename}")

print("done, saved in:", OUTPUT_FOLDER)
