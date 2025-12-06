import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration - Use absolute paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'docs', 'images')
INPUT_FILE = 'dailyActivity_merged.csv'

def perform_eda():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    file_path = os.path.join(DATA_DIR, INPUT_FILE)
    if not os.path.exists(file_path):
        print(f"Data file {file_path} not found. Skipping EDA.")
        return

    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    
    # Basic Stats
    print("Basic Statistics:")
    print(df.describe())
    
    # 1. Distribution of Total Steps
    plt.figure(figsize=(10, 6))
    sns.histplot(df['TotalSteps'], kde=True, bins=30)
    plt.title('Distribution of Daily Total Steps')
    plt.xlabel('Steps')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(OUTPUT_DIR, 'dist_steps.png'))
    plt.close()
    print("Saved dist_steps.png")

    # 2. Steps vs Calories
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='TotalSteps', y='Calories', hue='VeryActiveMinutes')
    plt.title('Total Steps vs Calories Burned')
    plt.xlabel('Steps')
    plt.ylabel('Calories')
    plt.savefig(os.path.join(OUTPUT_DIR, 'steps_vs_calories.png'))
    plt.close()
    print("Saved steps_vs_calories.png")

    # 3. Correlation Matrix
    # Select numeric columns relevant to activity
    cols = ['TotalSteps', 'TotalDistance', 'VeryActiveMinutes', 'SedentaryMinutes', 'Calories']
    corr = df[cols].corr()
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Matrix of Activity Metrics')
    plt.savefig(os.path.join(OUTPUT_DIR, 'correlation_matrix.png'))
    plt.close()
    print("Saved correlation_matrix.png")

if __name__ == "__main__":
    perform_eda()
