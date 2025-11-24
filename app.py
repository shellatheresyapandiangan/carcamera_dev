
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# =================== CONFIG =====================
st.set_page_config(
    page_title="MineVision AI - Advanced Fatigue Analytics",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        background-color: #003366;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #003366;
    }
    .insight-box {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #ff6b6b;
        margin: 10px 0;
    }
    .footer {
        text-align: center;
        padding: 20px;
        color: gray;
        font-size: 0.9em;
    }
    .risk-matrix {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
    }
    .risk-matrix th, .risk-matrix td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    .risk-matrix th {
        background-color: #f2f2f2;
    }
    .critical { background-color: #ffcccc; }
    .high { background-color: #ffebcc; }
    .medium { background-color: #ffffcc; }
    .low { background-color: #e6ffe6; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>⛏️ MineVision AI - Advanced Fatigue Analytics</h1><p>Proactive Safety Intelligence for Mining Operations</p></div>', unsafe_allow_html=True)

# =================== LOAD DATA ======================
@st.cache_data
def load_data():
    # Load data from the uploaded file
    try:
        df = pd.read_excel('manual fatique.xlsx', sheet_name=None, engine="openpyxl")
        
        # If the file has multiple sheets, concatenate them
        if isinstance(df, dict):
            df = pd.concat(df.values(), ignore_index=True)
        
        df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(" ", "_")

        # auto detect important columns
        col_operator = next((c for c in df.columns if "operator" in c or "driver" in c), None)
        col_shift = next((c for c in df.columns if "shift" in c), None)
        col_asset = next((c for c in df.columns if "asset" in c or "vehicle" in c or "fleet" in c), None)
        col_fleet_type = next((c for c in df.columns if "parent_fleet" in c), None)
        col_speed = next((c for c in df.columns if "speed" in c or "km/h" in c), None)

        # detect timestamps (using the actual column names from the provided file)
        start_time_cols = [c for c in df.columns if "gmt" in c.lower() and "wita" in c.lower()]
        # Assuming the first one is start and the second is end
        if len(start_time_cols) >= 2:
            df["start"] = pd.to_datetime(df[start_time_cols[0]], errors="coerce")
            df["end"] = pd.to_datetime(df[start_time_cols[1]], errors="coerce")
        elif len(start_time_cols) == 1:
            # If only one time column, assume it's start time and set end time to start + 1 minute as a placeholder
            df["start"] = pd.to_datetime(df[start_time_cols[0]], errors="coerce")
            df["end"] = df["start"] + pd.Timedelta(minutes=1)

        df["duration_sec"] = (df["end"] - df["start"]).dt.total_seconds()
        df["hour"] = df["start"].dt.hour
        df["date"] = df["start"].dt.date # Add date column for filtering
        df["day_of_week"] = df["start"].dt.day_name() # Add day of week for analysis
        df["week"] = df["start"].dt.isocalendar().week # Add week for trend analysis

        # Ensure shift is integer type and handle potential decimal values by rounding
        if col_shift:
            # Convert to numeric, then round to nearest integer, then convert to int64 to remove decimals
            df[col_shift] = pd.to_numeric(df[col_shift], errors='coerce').round().astype('Int64')

        return df, col_operator, col_shift, col_asset, col_fleet_type, col_speed
    except FileNotFoundError:
        st.error("File 'manual fatique.xlsx' not found. Please check the file path.")
        return pd.DataFrame(), None, None, None, None, None
    except Exception as e:
        st.error(f"Error loading  {e}")
        return pd.DataFrame(), None, None, None, None, None


df, col_operator, col_shift, col_asset, col_fleet_type, col_speed = load_data()

if df.empty:
    st.stop()

st.success("Data Loaded Successfully 🎉")

# =================== FILTERS =====================
st.sidebar.header("Filters")
# Date Range Filter: Default to "All" if no specific range is selected
if 'date' in df.columns:
    min_date = df['date'].min()
    max_date = df['date'].max()
    # Set default value to the full range initially
    date_range_default = (min_date, max_date)

    date_range_input = st.sidebar.date_input(
        "Select Date Range (Leave blank for All)",
        value=date_range_default, # Default to full range
        min_value=min_date,
        max_value=max_date
    )

    # Check if date_range_input is empty (user cleared the dates) or default full range is kept without interaction
    if not date_range_input or (len(date_range_input) == 2 and date_range_input[0] == min_date and date_range_input[1] == max_date):
        # If empty tuple or default full range, set to actual full range and mark as not explicitly filtered
        date_range = (min_date, max_date)
        date_filtered = False
    else:
        # If user selected a specific range, use it
        date_range = tuple(date_range_input)
        date_filtered = True
    # Apply date filter
    df = df[(df['date'] >= date_range[0]) & (df['date'] <= date_range[1])]

# =================== KPI METRICS =====================
st.subheader("📊 Executive Safety Dashboard")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Alerts", f"{len(df):,}")
col2.metric("Operators", df[col_operator].nunique() if col_operator else "-")
col3.metric("Assets", df[col_asset].nunique() if col_asset else "-")
col4.metric("Avg Duration (sec)", round(df["duration_sec"].mean(),2) if "duration_sec" in df.columns else "N/A")


# =================== TREND ANALYTICS =====================
st.subheader("📈 Fatigue Trend Analysis")

# Hourly
fig_hour = px.bar(
    df.groupby("hour").size().reset_index(name="alerts"),
    x="hour", y="alerts",
    title="⏰ Fatigue Alerts by Hour"
)
st.plotly_chart(fig_hour, width="stretch")

# Shift-Based
if col_shift:
    fig_shift = px.bar(
        df.groupby(col_shift).size().reset_index(name="alerts"),
        x=col_shift, y="alerts",
        title="👷 Fatigue Distribution by Shift"
    )
    st.plotly_chart(fig_shift, width="stretch")

    # hour inside shift heatmap
    heat_df = df.groupby([col_shift, "hour"]).size().reset_index(name="alerts")

    fig_heat = px.density_heatmap(
        heat_df,
        x="hour", y=col_shift, z="alerts",
        title="🔥 Heatmap Fatigue by Shift & Hour",
        color_continuous_scale="reds"
    )
    # Force the y-axis (shift) to be categorical to avoid decimal labels
    fig_heat.update_yaxes(type='category')
    st.plotly_chart(fig_heat, width="stretch")


# Operator Ranking
if col_operator:
    operator_counts = df[col_operator].value_counts().reset_index()
    operator_counts.columns = ["operator", "alerts"]
    fig_operator = px.bar(
        operator_counts,
        x="operator", y="alerts",
        title="🏆 Top Fatigue Alerts by Operator"
    )
    st.plotly_chart(fig_operator, width="stretch")


# =================== NEW CHARTS (Based on Mining Fatigue Factors) =====================
st.subheader("🔬 Advanced Mining Fatigue Analytics")

# 1. Day of Week Analysis (Workload Pattern)
if 'day_of_week' in df.columns:
    day_counts = df['day_of_week'].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    fig_day = px.bar(
        day_counts,
        x=day_counts.index, y=day_counts.values,
        title="📅 Fatigue Alerts by Day of Week (Workload Pattern)"
    )
    st.plotly_chart(fig_day, width="stretch")

# 2. Fleet Type Analysis (Task & Workload)
if col_fleet_type:
    fleet_counts = df[col_fleet_type].value_counts().reset_index()
    fleet_counts.columns = [col_fleet_type, "alerts"]
    fig_fleet = px.bar(
        fleet_counts,
        x=col_fleet_type, y="alerts",
        title="🚛 Fatigue Alerts by Fleet Type (Task Complexity)"
    )
    st.plotly_chart(fig_fleet, width="stretch")

# 3. Speed vs Hour Analysis (Environmental Factors & Workload)
if col_speed and "hour" in df.columns:
    # Remove rows with NaN speed values for this analysis
    speed_df = df.dropna(subset=[col_speed])
    if not speed_df.empty:
        fig_speed_hour = px.scatter(
            speed_df,
            x="hour", y=col_speed,
            title="🚗 Speed vs Hour of Day (Fatigue Events) - Environmental Factor",
            hover_data=[col_operator, col_asset]
        )
        st.plotly_chart(fig_speed_hour, width="stretch")

# 4. Duration vs Hour Analysis (Physiological Response)
if "duration_sec" in df.columns and "hour" in df.columns:
    fig_duration_hour = px.scatter(
        df,
        x="hour", y="duration_sec",
        title="⏱️ Fatigue Event Duration vs Hour of Day (Physiological Response)",
        hover_data=[col_operator, col_asset]
    )
    st.plotly_chart(fig_duration_hour, width="stretch")

# 5. Operator vs Shift Analysis (Shift Pattern Risk)
if col_operator and col_shift:
    op_shift_counts = df.groupby([col_operator, col_shift]).size().reset_index(name="alerts")
    fig_op_shift = px.bar(
        op_shift_counts,
        x=col_operator, y="alerts", color=col_shift,
        title="👤 Operator Fatigue Distribution by Shift (Shift Pattern Risk)"
    )
    st.plotly_chart(fig_op_shift, width="stretch")

# 6. Weekly Trend Analysis (Recovery Pattern)
if 'week' in df.columns:
    weekly_trend = df.groupby('week').size().reset_index(name='alerts')
    fig_weekly = px.line(
        weekly_trend,
        x='week', y='alerts',
        title="🗓️ Weekly Fatigue Trend (Recovery Pattern)"
    )
    st.plotly_chart(fig_weekly, width="stretch")

# 7. Speed Distribution Analysis (Task Complexity)
if col_speed:
    speed_df_clean = df.dropna(subset=[col_speed])
    if not speed_df_clean.empty:
        fig_speed_dist = px.histogram(
            speed_df_clean,
            x=col_speed,
            title="📏 Speed Distribution (Task Complexity Indicator)",
            nbins=20
        )
        st.plotly_chart(fig_speed_dist, width="stretch")


# =================== FATIGUE RISK ASSESSMENT =====================
st.subheader("⚠️ Mining-Specific Fatigue Risk Assessment")

# 1. Critical Hour Analysis (2-5 AM)
critical_hours = [2, 3, 4, 5]
critical_alerts = df[df['hour'].isin(critical_hours)]
critical_pct = (len(critical_alerts) / len(df)) * 100 if len(df) > 0 else 0

st.markdown(f"### 🌙 Critical Hour Risk (2-5 AM)")
st.metric("Critical Hour Alerts", f"{len(critical_alerts)}", f"{critical_pct:.1f}% of total alerts")
if critical_pct > 10:  # If more than 10% of alerts happen in critical hours
    st.warning(f"⚠️ High risk: {critical_pct:.1f}% of fatigue alerts occur during critical hours (2-5 AM). This is a known circadian dip period.")
else:
    st.info(f"✅ {critical_pct:.1f}% of alerts occur during critical hours. This is within acceptable range.")

# 2. High-Speed Fatigue Analysis (Environmental Risk)
if col_speed:
    high_speed_threshold = df[col_speed].quantile(0.75)  # Top 25% of speeds
    high_speed_fatigue = df[df[col_speed] >= high_speed_threshold]
    high_speed_pct = (len(high_speed_fatigue) / len(df)) * 100 if len(df) > 0 else 0
    
    st.markdown(f"### 🚀 High-Speed Fatigue Risk (Speed > {high_speed_threshold:.0f} km/h)")
    st.metric("High-Speed Fatigue Events", f"{len(high_speed_fatigue)}", f"{high_speed_pct:.1f}% of total alerts")
    if high_speed_pct > 20:  # If more than 20% of alerts happen at high speed
        st.warning(f"⚠️ High risk: {high_speed_pct:.1f}% of fatigue alerts occur at high speeds. This increases accident severity potential.")
    else:
        st.info(f"✅ {high_speed_pct:.1f}% of alerts occur at high speeds. This is within acceptable range.")

# 3. Shift Pattern Analysis
if col_shift:
    shift_counts = df[col_shift].value_counts()
    shift_alerts_by_hour = df.groupby([col_shift, 'hour']).size().reset_index(name='alerts')
    
    st.markdown(f"### 🔄 Shift Pattern Risk")
    for shift_val in shift_counts.index:
        shift_pct = (shift_counts[shift_val] / len(df)) * 100
        st.metric(f"Shift {shift_val} Alerts", f"{shift_counts[shift_val]}", f"{shift_pct:.1f}% of total alerts")
        if shift_pct > 50:  # If one shift has more than 50% of alerts
            st.warning(f"⚠️ Shift {shift_val} has disproportionately high alerts ({shift_pct:.1f}%). Review shift scheduling and workload.")
        else:
            st.info(f"✅ Shift {shift_val} alert distribution is acceptable ({shift_pct:.1f}%).")

# 4. Operator Risk Profiling
if col_operator:
    operator_alerts = df[col_operator].value_counts()
    top_risk_operators = operator_alerts.head(5)  # Top 5 operators by alerts
    
    st.markdown(f"### 👤 High-Risk Operator Identification")
    for op_name, count in top_risk_operators.items():
        op_pct = (count / len(df)) * 100
        st.metric(f"Operator: {op_name}", f"{count} alerts", f"{op_pct:.1f}% of total alerts")
        if op_pct > 5:  # If an operator has more than 5% of all alerts
            st.warning(f"⚠️ Operator {op_name} has high fatigue risk ({op_pct:.1f}% of alerts). Consider coaching or rest plan.")
        else:
            st.info(f"✅ Operator {op_name} fatigue risk is within acceptable range ({op_pct:.1f}%).")


# =================== FATIGUE RISK MATRIX =====================
st.subheader("📋 Fatigue Risk Matrix")

risk_matrix_data = [
    ["High fatigue + high-speed haul road", "Potential fatality", "Critical"],
    ["Moderate fatigue + decline haul road", "Serious injury", "High"],
    ["High fatigue + low-risk task", "Minor injury", "Medium"],
    ["Low fatigue + non-hazard task", "No injury", "Low"]
]

risk_df = pd.DataFrame(risk_matrix_data, columns=["Likelihood (Fatigue Level)", "Severity (Hazard Impact)", "Risk Tier"])

# Display risk matrix as a styled table
html_string = '<table class="risk-matrix"><thead><tr><th>Likelihood (Fatigue Level)</th><th>Severity (Hazard Impact)</th><th>Risk Tier</th></tr></thead><tbody>'
for _, row in risk_df.iterrows():
    risk_class = row["Risk Tier"].lower()
    html_string += f'<tr class="{risk_class}"><td>{row["Likelihood (Fatigue Level)"]}</td><td>{row["Severity (Hazard Impact)"]}</td><td>{row["Risk Tier"]}</td></tr>'
html_string += '</tbody></table>'

st.markdown(html_string, unsafe_allow_html=True)


# =================== AI INSIGHT ENGINE =====================
st.subheader("🤖 Automated Insight Summary")

insights = []

# Peak hour
if "hour" in df.columns and not df.empty:
    peak_hour = df["hour"].value_counts().idxmax()
    insights.append(f"⏱ Most fatigue risk occurs at **{peak_hour}:00** — likely due to circadian drop.")

# Risk shift
if col_shift and not df.empty:
    worst_shift = df[col_shift].value_counts().idxmax()
    insights.append(f"👷 Highest fatigue recorded in **Shift {worst_shift}** — review scheduling & workload.")

# Worst operator
if col_operator and not df.empty:
    worst_operator = df[col_operator].value_counts().idxmax()
    insights.append(f"⚠ Operator at highest risk: **{worst_operator}** — suggested coaching or rest plan.")

# Duration risk
if "duration_sec" in df.columns and not df.empty:
    avg_duration = df["duration_sec"].mean()
    if not pd.isna(avg_duration) and avg_duration > 10:
        insights.append("⏳ Long fatigue event duration suggests slow response — improve alerting training.")

# Critical hour insight
if "hour" in df.columns and not df.empty:
    critical_alerts = df[df['hour'].isin([2, 3, 4, 5])]
    if len(critical_alerts) > 0:
        critical_pct = (len(critical_alerts) / len(df)) * 100
        if critical_pct > 15:
            insights.append(f"🌙 **CRITICAL HOUR RISK**: {critical_pct:.1f}% of alerts occur during circadian low (2-5 AM). Consider enhanced monitoring during this period.")

# High-speed insight
if col_speed and not df.empty:
    high_speed_fatigue = df[df[col_speed] >= df[col_speed].quantile(0.75)] if not df[col_speed].dropna().empty else pd.DataFrame()
    if len(high_speed_fatigue) > 0:
        high_speed_pct = (len(high_speed_fatigue) / len(df)) * 100
        if high_speed_pct > 20:
            insights.append(f"🚀 **HIGH-SPEED RISK**: {high_speed_pct:.1f}% of fatigue events occur at high speeds, increasing accident severity potential.")

# Output insights
for i in insights:
    st.write("- " + i)


# ================= FOOTER ===========================
st.markdown("---")
st.markdown('<div class="footer">MineVision AI - Transforming Mining Safety with Intelligent Analytics | Contact: sales@minevision-ai.com</div>', unsafe_allow_html=True)
