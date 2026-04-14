import pdfplumber
import os
import re
from pathlib import Path

# ===== 配置区域 =====
PDF_FOLDER = "/Users/xinkewang/Desktop/U/Lingnan University/Course/Term2/CDS547_Intro to Large Language Models/group assignment/30篇计算机:社科:医学/计算机/原PDF"
OUTPUT_FOLDER = "/Users/xinkewang/Desktop/U/Lingnan University/Course/Term2/CDS547_Intro to Large Language Models/group assignment/30篇计算机:社科:医学/计算机/计科最小化清洗"
# ===================

def clean_text_minimal(text):
    """最小化清洗：只合并连字符，保留原始段落结构"""
    if not text:
        return ""
    
    # 1. 把连字符换行合并 (e.g., "dee-\nplearning" → "deep learning")
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    
    # 2. 什么都不做，直接返回（保留原始换行）
    return text

# 创建输出文件夹
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 找到所有PDF
pdf_files = list(Path(PDF_FOLDER).glob("*.pdf"))
# 按文件名排序，保证顺序一致
pdf_files.sort()
print(f"找到 {len(pdf_files)} 个PDF文件")

for i, pdf_path in enumerate(pdf_files, 1):
    print(f"处理 {i}/{len(pdf_files)}: {pdf_path.name}")
    
    # 提取文本
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    
    # 最小化清洗（只连字符合并）
    cleaned_text = clean_text_minimal(full_text)
    
    # 生成新文件名：paper_001.txt, paper_002.txt, ...
    new_filename = f"cs_paper_{i:03d}.txt"
    txt_path = os.path.join(OUTPUT_FOLDER, new_filename)
    
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)
    
    print(f"  已保存: {new_filename}")

print("全部完成！清洗后的TXT保存在:", OUTPUT_FOLDER)