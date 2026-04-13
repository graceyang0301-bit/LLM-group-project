import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configure paths
ROUGE_STAT_PATH = "../03_Results/rouge_statistics.csv"  # Aggregated scores
ROUGE_RAW_PATH = "../03_Results/rouge_results.csv"  # Detailed scores (30 papers)
PLOT_SAVE_DIR = "../03_Results/evaluation_plots/"  # Folder for saving plots


def init_plot_style():
    # Set consistent plot style (English font compatible)
    plt.rcParams["font.sans-serif"] = ["Arial", "Times New Roman"]
    plt.rcParams["axes.unicode_minus"] = False  # Fix negative sign display
    plt.rcParams["font.size"] = 11
    plt.rcParams["figure.dpi"] = 100
    sns.set_style("whitegrid")

    # Create plot folder if it doesn't exist
    if not os.path.exists(PLOT_SAVE_DIR):
        os.makedirs(PLOT_SAVE_DIR)
    print(f"Plots will be saved to: {PLOT_SAVE_DIR}")


def plot_rouge_f1_bar(stat_df):
    # Prepare data for bar plot
    plot_df = stat_df.reset_index()
    plot_df["strategy_short"] = plot_df["prompt_strategy"].replace(
        "LLM_Academic_Summary", "LLM Academic Summary"
    )

    # Create bar plot (3 metrics: Rouge-1, Rouge-2, Rouge-L)
    fig, ax = plt.subplots(figsize=(8, 6))
    x = range(len(plot_df))
    bar_width = 0.25  # Width of each bar

    # Plot bars for each metric
    bars1 = ax.bar(
        [i - bar_width for i in x],
        plot_df["rouge1_f1"],
        width=bar_width,
        label="ROUGE-1 F1",
        color="#1f77b4",
        alpha=0.8
    )
    bars2 = ax.bar(
        x,
        plot_df["rouge2_f1"],
        width=bar_width,
        label="ROUGE-2 F1",
        color="#ff7f0e",
        alpha=0.8
    )
    bars3 = ax.bar(
        [i + bar_width for i in x],
        plot_df["rougeL_f1"],
        width=bar_width,
        label="ROUGE-L F1",
        color="#2ca02c",
        alpha=0.8
    )

    # Add value labels on top of bars
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height + 0.002,  # Small offset above bar
                f"{height:.4f}",
                ha="center",
                va="bottom",
                fontsize=9
            )

    add_labels(bars1)
    add_labels(bars2)
    add_labels(bars3)

    # Customize plot labels and title
    ax.set_title("ROUGE-F1 Scores (30 Papers Across 3 Domains)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Prompt Strategy", fontsize=12)
    ax.set_ylabel("F1 Score", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(plot_df["strategy_short"])
    ax.legend(loc="upper right")

    # Adjust y-axis to avoid clipping labels
    ax.set_ylim(0, max(plot_df[["rouge1_f1", "rouge2_f1", "rougeL_f1"]].max()) * 1.2)

    # Save plot (high resolution)
    plt.tight_layout()
    plt.savefig(f"{PLOT_SAVE_DIR}/rouge_f1_bar.png", dpi=300, bbox_inches="tight")
    print("Bar plot saved: rouge_f1_bar.png")


def plot_rougeL_boxplot(raw_df):
    # Prepare data for boxplot
    raw_df["strategy_short"] = raw_df["prompt_strategy"].replace(
        "LLM_Academic_Summary", "LLM Academic Summary"
    )

    # Create boxplot (shows score distribution for 30 papers)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(
        x="strategy_short",
        y="rougeL_f1",
        hue="strategy_short",  # Fix seaborn future warning
        data=raw_df,
        palette="Set2",
        linewidth=1.5,
        legend=False  # No duplicate legend
    )

    # Customize plot
    ax.set_title("ROUGE-L F1 Distribution (30 Papers Across 3 Domains)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Prompt Strategy", fontsize=12)
    ax.set_ylabel("ROUGE-L F1 Score", fontsize=12)

    # Adjust y-axis to highlight distribution
    y_min = raw_df["rougeL_f1"].min() * 0.8 if raw_df["rougeL_f1"].min() > 0 else 0
    y_max = raw_df["rougeL_f1"].max() * 1.2
    ax.set_ylim(y_min, y_max)

    # Save plot
    plt.tight_layout()
    plt.savefig(f"{PLOT_SAVE_DIR}/rougeL_boxplot.png", dpi=300, bbox_inches="tight")
    print("Boxplot saved: rougeL_boxplot.png")


if __name__ == "__main__":
    try:
        init_plot_style()

        # Load ROUGE data
        stat_data = pd.read_csv(ROUGE_STAT_PATH, index_col="prompt_strategy")
        raw_data = pd.read_csv(ROUGE_RAW_PATH)

        # Generate plots
        plot_rouge_f1_bar(stat_data)
        plot_rougeL_boxplot(raw_data)

        print("\nAll plots generated successfully!")
    except Exception as e:
        print(f"Error generating plots: {str(e)}")
        exit(1)