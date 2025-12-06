# Tableau Dashboard Design Guide: "Neon Health" Command Center

## 🎨 Aesthetic Theme
**Style**: Cyberpunk / Dark Mode Fitness
**Background**: Deep Charcoal (`#1E1E1E`) or Black (`#000000`)
**Font**: Tableau Bold / Roboto (Clean, Sans-Serif)

### Color Palette
| Usage | Color | Hex Code |
| :--- | :--- | :--- |
| **Primary (Activity)** | Neon Cyan | `#00F0FF` |
| **Secondary (Sleep)** | Electric Purple | `#BD00FF` |
| **Accent (Calories)** | Hot Pink | `#FF0055` |
| **Good/High** | Fluorescent Green | `#39FF14` |
| **Warning/Low** | Alert Orange | `#FF5F1F` |
| **Text** | White / Light Gray | `#FFFFFF` / `#D3D3D3` |

---

## 📐 Layout Structure (Grid)

### 1. Header (Top 10%)
- **Title**: "FITBIT COMMAND CENTER" (Left aligned, Large, Bold)
- **Filters**: Date Range, User Segment (Right aligned)
- **Logo**: Optional (Top Left)

### 2. KPI Banners (Top 20%)
Create 4 "Big Number" cards. Use transparent backgrounds with glowing borders.
1.  **Avg Wellness Score**: Color code by value (Green > 70, Red < 50).
2.  **Total Steps**: Show vs. Target (10k).
3.  **Avg Sleep**: Hours.
4.  **Active Users**: Count of distinct IDs.

### 3. Main Trends (Middle 40%)
- **Left (60%)**: **"Activity Pulse"**
    - *Chart Type*: Dual Axis Line Chart.
    - *Axis 1*: Total Steps (Bar, Cyan).
    - *Axis 2*: Wellness Score (Line, White, Glowing).
    - *Insight*: See if wellness tracks with steps.
- **Right (40%)**: **"Calorie Burn Heatmap"**
    - *Chart Type*: Highlight Table / Heatmap.
    - *Rows*: Day of Week (Mon-Sun).
    - *Columns*: Hour of Day (if available) or User Segment.
    - *Color*: Intensity of Calories burned (Black to Hot Pink).

### 4. Deep Dive (Bottom 30%)
- **Left (50%)**: **"Sleep vs. Activity Scatter"**
    - *Chart Type*: Scatter Plot.
    - *X-Axis*: Total Steps.
    - *Y-Axis*: Minutes Asleep.
    - *Shape*: Circle (Opacity 60%).
    - *Insight*: Do active people sleep better?
- **Right (50%)**: **"Engagement Radar"**
    - *Chart Type*: Radar Chart (or Bar Chart if Radar is too complex).
    - *Metrics*: Very Active Mins, Light Active Mins, Sedentary Mins.
    - *Split by*: User Segment.

---

## 🧮 Calculated Fields (Copy & Paste)

**1. Wellness Score**
*(A composite metric to simplify health status)*
```tableau
([Total Steps] / 10000 * 40) + 
([Very Active Minutes] / 60 * 30) + 
([Calories] / 2500 * 30)
```

**2. Sleep Efficiency**
*(Percentage of time in bed actually spent sleeping)*
```tableau
IF [Total Time In Bed] > 0 THEN 
    [Total Minutes Asleep] / [Total Time In Bed]
ELSE 
    0 
END
```

**3. Weekend Flag**
```tableau
IF DATEPART('weekday', [ActivityDate]) = 1 OR DATEPART('weekday', [ActivityDate]) = 7 THEN 
    'Weekend' 
ELSE 
    'Weekday' 
END
```

---

## 🚀 Implementation Tips
1.  **Dark Mode**: Set the dashboard shading to `#1E1E1E`.
2.  **Clean Lines**: Remove all gridlines on charts. Keep only zero lines.
3.  **Tooltips**: Customize tooltips! Don't use the default. Make them read like a sentence:
    > *"On **<ActivityDate>**, User **<Id>** walked **<Total Steps>** steps and burned **<Calories>** calories."*
4.  **Interactivity**: Enable "Use as Filter" on the User Segment chart so clicking "Power User" filters the whole dashboard.
