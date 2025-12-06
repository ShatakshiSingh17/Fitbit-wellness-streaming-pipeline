import pandas as pd
import os
import glob

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw')
GOLD_DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'gold', 'tableau_ready')

def generate_tableau_datasets():
    print("Generating Tableau-ready datasets...")
    
    if not os.path.exists(GOLD_DATA_DIR):
        os.makedirs(GOLD_DATA_DIR)
        
    # --- Load Data ---
    activity_file = os.path.join(RAW_DATA_DIR, 'dailyActivity_merged.csv')
    sleep_file = os.path.join(RAW_DATA_DIR, 'sleepDay_merged.csv')
    
    if not os.path.exists(activity_file):
        print(f"Error: {activity_file} not found.")
        return

    print(f"Reading {activity_file}...")
    df_activity = pd.read_csv(activity_file)
    df_activity['ActivityDate'] = pd.to_datetime(df_activity['ActivityDate'], format='%m/%d/%Y')
    
    # Load Sleep Data (if available)
    if os.path.exists(sleep_file):
        print(f"Reading {sleep_file}...")
        df_sleep = pd.read_csv(sleep_file)
        # Sleep date often has time "4/12/2016 12:00:00 AM", so split it
        df_sleep['SleepDay'] = pd.to_datetime(df_sleep['SleepDay']) 
        df_sleep['ActivityDate'] = df_sleep['SleepDay'] # Rename for merge
        
        # Aggregate sleep by day (sometimes multiple records per day)
        df_sleep_agg = df_sleep.groupby(['Id', 'ActivityDate']).agg({
            'TotalSleepRecords': 'sum',
            'TotalMinutesAsleep': 'sum',
            'TotalTimeInBed': 'sum'
        }).reset_index()
    else:
        print("Warning: Sleep data not found. Creating empty sleep columns.")
        df_sleep_agg = pd.DataFrame(columns=['Id', 'ActivityDate', 'TotalMinutesAsleep', 'TotalTimeInBed'])

    # --- Merge Activity & Sleep ---
    print("Merging Activity and Sleep data...")
    df_merged = pd.merge(df_activity, df_sleep_agg, on=['Id', 'ActivityDate'], how='left')
    
    # Fill NaN sleep values with 0
    df_merged['TotalMinutesAsleep'] = df_merged['TotalMinutesAsleep'].fillna(0)
    df_merged['TotalTimeInBed'] = df_merged['TotalTimeInBed'].fillna(0)

    # --- Enrich Data ---
    
    # 1. User Segment (Based on average steps)
    avg_steps = df_merged.groupby('Id')['TotalSteps'].mean().reset_index()
    def get_segment(steps):
        if steps < 5000: return 'Sedentary'
        elif steps < 10000: return 'Active'
        else: return 'Power User'
    avg_steps['UserSegment'] = avg_steps['TotalSteps'].apply(get_segment)
    
    df_merged = pd.merge(df_merged, avg_steps[['Id', 'UserSegment']], on='Id', how='left')

    # 2. Wellness Score
    # Formula: (Steps/10000 * 0.4) + (ActiveMins/60 * 0.3) + (SleepHours/7 * 0.3) * 100
    # Capped at 100
    df_merged['WellnessScore'] = (
        (df_merged['TotalSteps'] / 10000 * 40) + 
        (df_merged['VeryActiveMinutes'] / 60 * 30) + 
        ((df_merged['TotalMinutesAsleep'] / 60) / 7 * 30)
    )
    
    # --- Select Final Columns ---
    final_columns = [
        'Id', 
        'ActivityDate', 
        'TotalSteps', 
        'Calories', 
        'VeryActiveMinutes', 
        'LightlyActiveMinutes', 
        'SedentaryMinutes', 
        'TotalMinutesAsleep', 
        'TotalTimeInBed', 
        'UserSegment',
        'WellnessScore' # Added bonus
    ]
    
    # Filter only columns that exist (in case of schema changes)
    cols_to_export = [c for c in final_columns if c in df_merged.columns]
    
    df_final = df_merged[cols_to_export]
    
    # Export
    output_path = os.path.join(GOLD_DATA_DIR, 'daily_wellness_kpi.csv')
    df_final.to_csv(output_path, index=False)
    print(f"Created consolidated file: {output_path}")
    print(f"Total Rows: {len(df_final)}")
    print("Columns:", df_final.columns.tolist())
    
    print("Done! Import this single file into Tableau.")

if __name__ == "__main__":
    generate_tableau_datasets()
