import pandas as pd
import numpy as np

# Configure paths (matches your manual evaluation file)
INPUT_PATH = "../01_Input_Data/manual_evaluation.xlsx"  # 30-paper manual scores
OUTPUT_PATH = "../03_Results/manual_evaluation_stat.csv"  # Aggregated results


def validate_manual_data(df):
    # Required columns for manual evaluation
    required_cols = [
        "paper_id", "prompt_strategy",
        "completeness", "accuracy", "fluency", "academic", "overall"
    ]

    # Check for missing columns
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

    # Check score range (1-5)
    score_cols = ["completeness", "accuracy", "fluency", "academic", "overall"]
    for col in score_cols:
        if not df[col].between(1, 5).all():
            raise ValueError(f"Invalid scores in {col} (must be 1-5)")

    # Check for empty values
    df = df.dropna(subset=required_cols)
    if len(df) == 0:
        raise ValueError("No valid manual evaluation data found!")

    return df


def aggregate_manual_scores(df):
    # Calculate average scores by prompt strategy
    stat_df = df.groupby("prompt_strategy").agg({
        "completeness": ["mean", "std"],  # Mean + standard deviation
        "accuracy": ["mean", "std"],
        "fluency": ["mean", "std"],
        "academic": ["mean", "std"],
        "overall": ["mean", "std"],
        "paper_id": "count"  # Number of valid records
    }).round(4)

    # Flatten multi-level columns (e.g., "completeness_mean" instead of ("completeness", "mean"))
    stat_df.columns = [f"{col[0]}_{col[1]}" for col in stat_df.columns]
    stat_df.rename(columns={"paper_id_count": "valid_records"}, inplace=True)

    # Reorder columns for readability
    column_order = [
        "completeness_mean", "completeness_std",
        "accuracy_mean", "accuracy_std",
        "fluency_mean", "fluency_std",
        "academic_mean", "academic_std",
        "overall_mean", "overall_std",
        "valid_records"
    ]
    stat_df = stat_df[column_order]

    return stat_df


def process_manual_evaluation():
    # Load manual evaluation data
    try:
        df = pd.read_excel(INPUT_PATH, engine="openpyxl")
        print(f"Loaded manual evaluation data: {len(df)} records")
    except Exception as e:
        raise FileNotFoundError(f"Failed to load manual evaluation file: {str(e)}")

    # Validate data quality
    df_valid = validate_manual_data(df)
    print(f"Valid records after cleaning: {len(df_valid)}")

    # Calculate aggregated scores
    stat_df = aggregate_manual_scores(df_valid)

    # Save results
    stat_df.to_csv(OUTPUT_PATH, encoding="utf-8")
    print(f"\nAggregated manual evaluation results saved to: {OUTPUT_PATH}")

    # Print summary
    print("\n=== Average Manual Evaluation Scores (1-5) ===")
    print(stat_df[["completeness_mean", "accuracy_mean", "fluency_mean", "academic_mean", "overall_mean"]])
    print(f"\nValid records per strategy: {stat_df['valid_records'].to_dict()}")

    return stat_df


if __name__ == "__main__":
    try:
        process_manual_evaluation()
        print("\nManual evaluation processing completed successfully!")
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)