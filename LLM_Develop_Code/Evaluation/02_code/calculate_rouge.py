import pandas as pd
from rouge_score import rouge_scorer
import numpy as np

# ===================== Configure Paths =====================
EVAL_DATA_PATH = "../03_Results/eval_dataset.csv"  # Official abstracts (ID: bio_bio_paper_001, etc.)
LLM_SUMMARY_PATH = "../01_Input_Data/30_Papers_LLM_Summaries_Final.xlsx"  # LLM abstracts (ID: soc_paper_001, etc.)
ROUGE_RESULT_PATH = "../03_Results/rouge_results.csv"
ROUGE_STAT_PATH = "../03_Results/rouge_statistics.csv"


# ===================== 1. Load & Merge Data (Fix Duplicate Prefix) =====================
def load_and_merge_data(eval_path, llm_path):
    # Load official abstracts & fix ID format (e.g., bio_bio_paper_001 → bio_paper_001)
    eval_df = pd.read_csv(eval_path)
    eval_df["paper_id"] = eval_df["paper_id"].astype(str).str.strip()

    # Core fix: Remove duplicate domain prefix (e.g., "bio_bio_" → "bio_")
    eval_df["paper_id_fixed"] = eval_df["paper_id"].str.replace(r"^([a-z]{2,3})_\1_", r"\1_", regex=True)
    # Regex explanation: ^([a-z]{2,3})_\1_ → Matches "bio_bio_", "cs_cs_", "soc_soc_" and replaces with "bio_", "cs_", "soc_"

    print(f"Fixed official ID examples (before → after):")
    for i in range(3):
        print(f"  {eval_df['paper_id'].iloc[i]} → {eval_df['paper_id_fixed'].iloc[i]}")

    # Load LLM abstracts (correct ID format: soc_paper_001, etc.)
    llm_df = pd.read_excel(llm_path, engine="openpyxl")
    llm_id_col = llm_df.columns[0]  # Auto-detect ID column
    llm_df.rename(columns={llm_id_col: "paper_id_fixed"}, inplace=True)  # Match fixed ID column
    llm_df["paper_id_fixed"] = llm_df["paper_id_fixed"].astype(str).str.strip()

    print(f"\nLLM ID examples (top 3): {llm_df['paper_id_fixed'].head(3).tolist()}")

    # Keep only necessary columns
    llm_df = llm_df[["paper_id_fixed", "LLM_Academic_Summary"]].copy()
    llm_df = llm_df.dropna(subset=["LLM_Academic_Summary"])
    llm_df = llm_df[llm_df["LLM_Academic_Summary"].str.strip() != ""]

    # Merge by fixed ID (now official and LLM IDs match)
    merged_df = pd.merge(eval_df, llm_df, on="paper_id_fixed", how="inner")
    # Keep original paper_id and necessary columns for downstream use
    merged_df = merged_df[["paper_id", "official_abstract", "LLM_Academic_Summary"]]

    # Print merge summary
    print("\n=== Data Merge Summary ===")
    print(f"Total official abstracts: {len(eval_df)}")
    print(f"Total LLM abstracts: {len(llm_df)}")
    print(f"Matching papers (for ROUGE): {len(merged_df)}")
    print("==========================")

    if len(merged_df) == 0:
        raise ValueError("No matches after fix! Check if official ID prefix is 'bio_', 'cs_', or 'soc_'")

    return merged_df


# ===================== 2. Initialize ROUGE Scorer =====================
def init_rouge_scorer():
    return rouge_scorer.RougeScorer(
        rouge_types=["rouge1", "rouge2", "rougeL"],
        use_stemmer=True  # Suitable for English abstracts
    )


# ===================== 3. Calculate ROUGE Scores =====================
def calculate_rouge(merged_df, scorer):
    rouge_results = []

    for idx, row in merged_df.iterrows():
        paper_id = row["paper_id"]
        official_abs = row["official_abstract"].strip()
        generated_abs = row["LLM_Academic_Summary"].strip()

        if not official_abs or not generated_abs:
            print(f"Warning: Skipping {paper_id} (empty abstract)")
            continue

        scores = scorer.score(official_abs, generated_abs)
        rouge_results.append({
            "paper_id": paper_id,
            "prompt_strategy": "LLM_Academic_Summary",
            "rouge1_precision": round(scores["rouge1"].precision, 4),
            "rouge1_recall": round(scores["rouge1"].recall, 4),
            "rouge1_f1": round(scores["rouge1"].fmeasure, 4),
            "rouge2_precision": round(scores["rouge2"].precision, 4),
            "rouge2_recall": round(scores["rouge2"].recall, 4),
            "rouge2_f1": round(scores["rouge2"].fmeasure, 4),
            "rougeL_precision": round(scores["rougeL"].precision, 4),
            "rougeL_recall": round(scores["rougeL"].recall, 4),
            "rougeL_f1": round(scores["rougeL"].fmeasure, 4)
        })

    rouge_df = pd.DataFrame(rouge_results)
    rouge_df.to_csv(ROUGE_RESULT_PATH, index=False, encoding="utf-8")
    print(f"\nDetailed ROUGE results saved to: {ROUGE_RESULT_PATH}")
    return rouge_df


# ===================== 4. Aggregate ROUGE Scores =====================
def aggregate_rouge_scores(rouge_df):
    stat_df = rouge_df.groupby("prompt_strategy").agg({
        "rouge1_f1": "mean",
        "rouge2_f1": "mean",
        "rougeL_f1": "mean"
    }).round(4)

    stat_df.to_csv(ROUGE_STAT_PATH, encoding="utf-8")
    print("\n=== Average ROUGE F1 Scores ===")
    print(stat_df)
    print(f"\nAggregated results saved to: {ROUGE_STAT_PATH}")
    return stat_df


# ===================== Main Execution =====================
if __name__ == "__main__":
    try:
        merged_data = load_and_merge_data(EVAL_DATA_PATH, LLM_SUMMARY_PATH)
        rouge_scorer = init_rouge_scorer()
        detailed_scores = calculate_rouge(merged_data, rouge_scorer)
        aggregate_rouge_scores(detailed_scores)
        print("\nROUGE calculation completed successfully!")
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)