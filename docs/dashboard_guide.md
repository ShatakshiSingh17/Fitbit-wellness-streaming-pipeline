# Dashboard Creation Guide

This guide outlines how to build the **Fitbit Wellness Analytics Dashboard** using the processed data in `data/gold`.

## Data Source
- **Fact Table**: `data/gold/daily_activity_kpi` (or `fact_daily_activity` export)
- **Dimensions**: `dim_user`, `dim_date` (if exported to CSV/Parquet)

## Dashboard Pages

### 1. Executive Summary
**Goal**: High-level overview of user wellness.
- **KPI Cards**:
    - Average Daily Steps (Target: 10,000)
    - Average Sleep Hours (Target: 8 hrs)
    - Active User Count
- **Charts**:
    - **Wellness Score Distribution** (Histogram): Show how many users fall into "Excellent", "Good", "Fair", "Poor".
    - **Engagement Segments** (Pie Chart): High vs. Low engagement users.

### 2. Activity Analytics
**Goal**: Deep dive into physical activity trends.
- **Line Chart**: Average Steps vs. Calories Burned over time.
- **Bar Chart**: Activity Intensity Breakdown (Very Active vs. Sedentary minutes) by Day of Week.
- **Scatter Plot**: Steps vs. Calories (Identify efficiency).

### 3. Sleep & Recovery
**Goal**: Analyze sleep patterns.
- **Line Chart**: Average Sleep Duration vs. Time in Bed (Efficiency gap).
- **Correlation**: Sleep Duration vs. Next Day Steps (Does more sleep lead to more activity?).

## Implementation Steps (Power BI Example)
1. **Get Data**: Select "Parquet" or "CSV" source. Point to `data/gold`.
2. **Model**: Ensure relationships are set (User ID -> User ID).
3. **Measures**: Create DAX measures for `Avg Steps = AVERAGE(TotalSteps)`.
4. **Visualize**: Drag and drop fields to create the charts above.
