# ====================== 1. Import Required Libraries ======================
import pandas as pd  # For reading/writing Excel files
from zhipuai import ZhipuAI  # For connecting to GLM-4-Flash API
import time  # To avoid frequent API calls (prevent rate limits)

# ====================== 2. Initialize GLM-4-Flash with Your API Key ======================
client = ZhipuAI(api_key="e2ee469be866476ba303b60714d97475.qgjHQMISad2TnO2u")

# ====================== 3. Load 3 Excel Files & Extract 10 Papers Each ======================

excel_files = [
    r"D:\547\soc_cleaned.xlsx",      
    r"D:\547\bio_cleaned.xlsx",             
    r"D:\547\cs_cleaned.xlsx"              
]

all_papers = []  

for file_path in excel_files:
    print(f"\n📂 Reading file: {file_path}")
    df_temp = pd.read_excel(file_path)
    df_10 = df_temp.head(10)
    all_papers.append(df_10)

df = pd.concat(all_papers, ignore_index=True)

paper_texts = df['source_text (main)'].tolist()
total_papers = len(paper_texts) 

# ====================== 4. Batch Generate Summaries for All 30 Papers ======================
generated_summaries = []  # Empty list to store all summaries

for paper_index, paper_content in enumerate(paper_texts, start=1):
    print(f"\n📄 Processing Paper {paper_index}/{total_papers}...")
    
    # English Prompt: Academic Summary Instruction (optimized for LLM)
    academic_prompt = f"""
You are a professional academic summary expert specializing in scientific papers. Generate a concise, accurate summary for the following paper with the requirements below:

1. Content Requirements:
   - Research Background & Core Problem: What gap does this paper address? What problem does it solve?
   - Core Methodology: What key methods, frameworks, or experiments does the paper use?
   - Key Results: What are the main findings (e.g., data, metric improvements, comparisons to SOTA)?
   - Conclusion & Value: What is the academic contribution or practical application of this work?

2. Format Requirements:
   - Length: 150-250 words (concise, no redundancy)
   - Tone: Formal academic English (no colloquial language)
   - Accuracy: 100% based on the original paper (no fabricated information or overstated contributions)

Original Paper Content:
{paper_content}

Please output the final academic summary:
    """
    
    # Call GLM-4-Flash API to generate summary (with error handling)
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",  # Free model (fixed)
            messages=[{"role": "user", "content": academic_prompt}],
            temperature=0.2,  # Low temperature = stable, accurate output
            top_p=0.9
        )
        # Extract the generated summary
        summary = response.choices[0].message.content
        generated_summaries.append(summary)
        print(f"✅ Paper {paper_index} Summary Generated Successfully!")
        
        # 2-second delay (avoids hitting free API rate limits)
        time.sleep(2)
    
    # Handle errors (e.g., network issues, API limits) without stopping the loop
    except Exception as error:
        error_message = f"Generation Failed: {str(error)[:50]}..."  # Truncate long errors
        generated_summaries.append(error_message)
        print(f"❌ Paper {paper_index} Summary Failed. Reason: {error_message}")
        time.sleep(3)  # Longer delay after error to reset API

# ====================== 5. Save Results to Excel ======================
# Add summaries to the original Excel file (new column: "LLM_Academic_Summary")
df['LLM_Academic_Summary'] = generated_summaries

# Save output file to your desktop (English filename for assignment)
output_file_path = r"D:\547\30_Papers_LLM_Summaries_Final.xlsx"
df.to_excel(output_file_path, index=False, engine='openpyxl')

# Final completion message (English)
print(f"\n" + "="*70)
print(f"🎉 All {total_papers} Papers Processed Successfully!")
print(f"📁 Output File Saved To: {output_file_path}")
print(f"✅ Open the Excel file to view summaries in the 'LLM_Academic_Summary' column.")
print(f"="*70)
