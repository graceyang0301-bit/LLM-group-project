import pandas as pd
import os

# Configure paths (matches your 01_Input_Data folder structure)
INPUT_FILES = {
    "bio": "../01_Input_Data/bio_cleaned.xlsx",  # Biology: 10 papers
    "cs": "../01_Input_Data/cs_cleaned.xlsx",  # Computer Science: 10 papers
    "soc": "../01_Input_Data/soc_cleaned.xlsx"  # Sociology: 10 papers
}
OUTPUT_PATH = "../03_Results/eval_dataset.csv"  # Output: 30 papers total


def preprocess_data():
    all_papers = []

    # Process each domain file
    for domain, file_path in INPUT_FILES.items():
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file missing: {file_path}")

        # Read Excel file
        df = pd.read_excel(file_path, engine="openpyxl")

        # Standardize column names (match downstream scripts)
        required_columns = ["ID", "target_text (Abstract)"]
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"File {file_path} missing required columns: {required_columns}")

        df.rename(columns={
            "ID": "paper_id",
            "target_text (Abstract)": "official_abstract"
        }, inplace=True)

        # Keep only essential columns
        df = df[["paper_id", "official_abstract"]].copy()

        # Add domain prefix to paper_id (ensure uniqueness: e.g., bio_001, cs_001)
        df["paper_id"] = df["paper_id"].apply(
            lambda x: f"{domain}_{int(x):03d}" if pd.api.types.is_numeric_dtype(type(x))
            else f"{domain}_{str(x).zfill(3)}"
        )

        # Clean abstract text (remove extra spaces/newlines)
        df["official_abstract"] = df["official_abstract"].astype(str).str.strip()
        df["official_abstract"] = df["official_abstract"].str.replace(r"\s+", " ", regex=True)

        # Remove empty abstracts
        df = df[df["official_abstract"] != ""].dropna(subset=["official_abstract"])

        all_papers.append(df)
        print(f"Processed {domain.upper()} domain: {len(df)} papers")

    # Combine all 3 domains into one DataFrame
    combined_df = pd.concat(all_papers, ignore_index=True)

    # Validate total paper count
    if len(combined_df) != 30:
        print(f"Warning: Total papers = {len(combined_df)} (expected 30)")

    # Save cleaned data
    combined_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"\nPreprocessing completed!")
    print(f"Total cleaned papers: {len(combined_df)}")
    print(f"Output saved to: {OUTPUT_PATH}")

    return combined_df


if __name__ == "__main__":
    preprocess_data()