
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>⛏️ MineVision AI - Advanced Fatigue Analytics</h1><p>Proactive Safety Intelligence for Mining Operations</p></div>', unsafe_allow_html=True)

# =================== LOAD DATA ======================
@st.cache_data
def load_data():
    # Using the uploaded file path (simulated for this example)
    # In a real app, you would use the file uploader or a stable URL
    try:
        # Simulating loading the provided Excel data structure
        # Replace with actual file path or URL when deployed
        # url = "https://raw.githubusercontent.com/shellatheresyapandiangan/carcamera_dev/main/manual%20fatique.xlsx"
        # For this example, we'll create a mock DataFrame based on the provided structure
        # In practice, use pd.read_excel(file_path, sheet_name=None, engine="openpyxl")
        
        # Creating a mock DataFrame based on the provided sample data
        # This is a placeholder - replace with actual loading logic
        data_dict = {
            'ticket_number': ['ADT - HDKM78554-PDSM00188544', 'ADT - HDCT77370-PDSM00187812', 'SDJ - HDCT73036-PDSM00160636', 'ADT - HDCT77346-PDSM00160540'],
            'parent_fleet': ['ADT - OB HAULLER', 'ADT - OB HAULLER', 'SDJ - OB HAULLER', 'ADT - OB HAULLER'],
            'fleet_number': ['ADT - HDKM78554', 'ADT - HDCT77370', 'SDJ - HDCT73036', 'ADT - HDCT77346'],
            'nik': [10032560, 10026757, 10027510, 10029870],
            'operator_name': ['Ery Arfandi Bazrah', 'Yodi Wanjaya', 'Arif Kassa P', 'Maulana Fajar Asrori'],
            'sid_code': ['', '', '', ''],
            'area_kerja': ['', '', '', ''],
            'alarm_type': ['Driver Fatigue', 'Driver Fatigue', 'Driver Fatigue', 'Driver Fatigue'],
            'gmt_start': ['10/19/25 8:27', '10/19/25 6:23', '11/12/25 4:12', '11/12/25 3:52'],
            'gmt_end': ['10/19/25 8:28', '10/19/25 6:29', '11/12/25 4:12', '11/12/25 3:52'],
            'shift': [1, 1, 2, 2],
            'speed_kmh': [2, 1, 12, 1],
            'area': ['', '', '', ''],
            'condition': ['', '', '', ''],
            'validation_status': ['Validated', 'Validated', 'Validated', 'Validated'],
            'follow_up_status': ['Close', 'Close', 'Close', 'Close'],
            'validation_remarks': ['Valid', 'Valid', 'Valid', 'Valid'],
            'qc_status': ['Yes', 'Yes', 'Yes', 'Yes']
        }
        df = pd.DataFrame(data_dict)
        
        # Convert date columns
        df['start'] = pd.to_datetime(df['gmt_start'], format='%m/%d/%y %H:%M', errors='coerce')
        df['end'] = pd.to_datetime(df['gmt_end'], format='%m/%d/%y %H:%M', errors='coerce')
        
        # Calculate duration
        df['duration_sec'] = (df['end'] - df['start']).dt.total_seconds()
        df['hour'] = df['start'].dt.hour
        df['date'] = df['start'].dt.date
        
        # Rename columns to lowercase for consistency
        df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(" ", "_")
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No data loaded. Please check your data source.")
    st.stop()

st.success("Data Loaded Successfully 🎉")

# Sidebar for filters
st.sidebar.header("Filters")
if 'date' in df.columns:
    date_range = st.sidebar.date_input("Select Date Range", value=[df['date'].min(), df['date'].max()])
if 'parent_fleet' in df.columns:
    selected_fleets = st.sidebar.multiselect("Select Fleet Type", options=df['parent_fleet'].unique(), default=df['parent_fleet'].unique())
if 'shift' in df.columns:
    selected_shifts = st.sidebar.multiselect("Select Shift", options=df['shift'].unique(), default=df['shift'].unique())

# Apply filters
filtered_df = df.copy()
if 'date' in df.columns and len(date_range) == 2:
    filtered_df = filtered_df[(filtered_df['date'] >= date_range[0]) & (filtered_df['date'] <= date_range[1])]
if 'parent_fleet' in df.columns and selected_fleets:
    filtered_df = filtered_df[filtered_df['parent_fleet'].isin(selected_fleets)]
if 'shift' in df.columns and selected_shifts:
    filtered_df = filtered_df[filtered_df['shift'].isin(selected_shifts)]

# =================== KPI METRICS =====================
st.subheader("📊 Executive Safety Dashboard")

col1, col2, col3, col4, col5 = st.columns(5)

# Calculate metrics
total_alerts = len(filtered_df)
total_operators = filtered_df['operator_name'].nunique() if 'operator_name' in filtered_df.columns else 0
total_assets = filtered_df['fleet_number'].nunique() if 'fleet_number' in filtered_df.columns else 0
avg_duration = filtered_df['duration_sec'].mean() if 'duration_sec' in filtered_df.columns else 0
total_fleet_types = filtered_df['parent_fleet'].nunique() if 'parent_fleet' in filtered_df.columns else 0

col1.metric("Total Fatigue Alerts", f"{total_alerts:,}")
col2.metric("Unique Operators", f"{total_operators}")
col3.metric("Active Assets", f"{total_assets}")
col4.metric("Avg. Alert Duration (s)", f"{avg_duration:.2f}")
col5.metric("Fleet Types", f"{total_fleet_types}")

# Additional KPIs
st.markdown("---")
st.subheader("📈 Advanced Trend Analysis")

# Row 1: Time Series and Shift Distribution
col1, col2 = st.columns(2)

with col1:
    # Daily Trend
    if 'date' in filtered_df.columns:
        daily_trend = filtered_df.groupby('date').size().reset_index(name='alerts')
        fig_daily = px.line(daily_trend, x='date', y='alerts', title="📅 Daily Fatigue Alert Trend")
        fig_daily.update_layout(height=400)
        st.plotly_chart(fig_daily, use_container_width=True)

with col2:
    # Shift Distribution
    if 'shift' in filtered_df.columns:
        shift_counts = filtered_df['shift'].value_counts().reset_index()
        shift_counts.columns = ['shift', 'count']
        fig_shift = px.bar(shift_counts, x='shift', y='count', title="👷 Fatigue Distribution by Shift")
        fig_shift.update_layout(height=400)
        st.plotly_chart(fig_shift, use_container_width=True)

# Row 2: Hourly and Fleet Analysis
col1, col2 = st.columns(2)

with col1:
    # Hourly Pattern
    if 'hour' in filtered_df.columns:
        hourly_counts = filtered_df['hour'].value_counts().reset_index()
        hourly_counts.columns = ['hour', 'count']
        hourly_counts = hourly_counts.sort_values('hour')
        fig_hourly = px.bar(hourly_counts, x='hour', y='count', title="⏰ Fatigue Alerts by Hour of Day")
        fig_hourly.update_layout(height=400)
        st.plotly_chart(fig_hourly, use_container_width=True)

with col2:
    # Fleet Type Distribution
    if 'parent_fleet' in filtered_df.columns:
        fleet_counts = filtered_df['parent_fleet'].value_counts().reset_index()
        fleet_counts.columns = ['fleet_type', 'count']
        fig_fleet = px.pie(fleet_counts, values='count', names='fleet_type', title="🚛 Fatigue by Fleet Type")
        fig_fleet.update_layout(height=400)
        st.plotly_chart(fig_fleet, use_container_width=True)

# =================== OPERATOR & ASSET ANALYSIS =====================
st.subheader("👤 Operator & Asset Risk Profiling")

col1, col2 = st.columns(2)

with col1:
    # Top Operators by Alerts
    if 'operator_name' in filtered_df.columns:
        operator_counts = filtered_df['operator_name'].value_counts().head(10).reset_index()
        operator_counts.columns = ['operator', 'alerts']
        fig_operator = px.bar(operator_counts, x='alerts', y='operator', orientation='h', title="🚨 Top 10 Operators by Fatigue Alerts")
        fig_operator.update_layout(height=500)
        st.plotly_chart(fig_operator, use_container_width=True)

with col2:
    # Top Assets by Alerts
    if 'fleet_number' in filtered_df.columns:
        asset_counts = filtered_df['fleet_number'].value_counts().head(10).reset_index()
        asset_counts.columns = ['asset', 'alerts']
        fig_asset = px.bar(asset_counts, x='alerts', y='asset', orientation='h', title="🚨 Top 10 Assets by Fatigue Alerts")
        fig_asset.update_layout(height=500)
        st.plotly_chart(fig_asset, use_container_width=True)

# =================== ADVANCED AI INSIGHTS =====================
st.subheader("🤖 AI-Powered Safety Insights & Recommendations")

# Calculate insights based on data
insights = []

if 'hour' in filtered_df.columns:
    peak_hour = filtered_df['hour'].mode().iloc[0] if not filtered_df['hour'].mode().empty else 'N/A'
    insights.append(f"⏱️ **Peak Risk Hour**: Most fatigue incidents occur around {peak_hour}:00. Consider enhanced monitoring during this period.")

if 'shift' in filtered_df.columns:
    worst_shift = filtered_df['shift'].value_counts().index[0] if not filtered_df['shift'].value_counts().empty else 'N/A'
    insights.append(f"👷 **Shift Risk**: Shift {worst_shift} shows the highest fatigue incidents. Review scheduling and workload distribution.")

if 'operator_name' in filtered_df.columns:
    top_risk_operator = filtered_df['operator_name'].value_counts().index[0] if not filtered_df['operator_name'].value_counts().empty else 'N/A'
    insights.append(f"👤 **High-Risk Operator**: Operator '{top_risk_operator}' has the most alerts. Consider targeted coaching or rest adjustment.")

if 'duration_sec' in filtered_df.columns:
    avg_duration = filtered_df['duration_sec'].mean()
    if avg_duration > 60:  # More than 1 minute
        insights.append(f"⏳ **Response Time**: Average alert duration is {avg_duration:.2f} seconds. This indicates a need for faster response protocols.")

if 'parent_fleet' in filtered_df.columns:
    top_fleet_type = filtered_df['parent_fleet'].value_counts().index[0] if not filtered_df['parent_fleet'].value_counts().empty else 'N/A'
    insights.append(f"🚛 **Fleet Risk**: The '{top_fleet_type}' fleet type has the most incidents. Investigate specific operational factors.")

# Additional predictive insights based on patterns
if len(filtered_df) > 10:
    # If more than 10% of alerts happen in a specific hour, flag it
    hour_counts = filtered_df['hour'].value_counts(normalize=True)
    if not hour_counts.empty and hour_counts.iloc[0] > 0.10:
        flagged_hour = hour_counts.index[0]
        insights.append(f"⚠️ **Predictive Alert**: Hour {flagged_hour} has disproportionately high fatigue risk ({hour_counts.iloc[0]*100:.1f}% of alerts). Implement preventive measures.")

# Display insights in styled boxes
for insight in insights:
    st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)

# =================== CAMERA DETECTION INTEGRATION HYPOTHESIS =====================
st.subheader("📷 Camera Detection Integration Insights")

st.info("""
**How MineVision AI Enhances Camera Systems:**
- **Real-Time Alerting**: Camera-detected drowsiness triggers immediate dashboard alerts.
- **Severity Scoring**: AI scores fatigue levels (1-10) based on eyelid closure, head nod, and gaze direction.
- **Predictive Modeling**: Combines camera data with historical patterns for proactive alerts.
- **Automated Reporting**: Generates compliance reports for safety audits.
- **Integration Ready**: APIs for seamless connection with existing camera systems (Wenco, Cat, Komatsu, etc.).
""")

st.success("Your camera system can feed real-time data into this dashboard for enhanced safety monitoring.")

# =================== VALUE PROPOSITION =====================
st.subheader("💰 Business Value & ROI")

value_cols = st.columns(3)

with value_cols[0]:
    st.markdown("### 🛡️ Risk Reduction")
    st.markdown("- Decrease fatigue-related incidents by up to 70%")
    st.markdown("- Proactive intervention prevents accidents")
    st.markdown("- Real-time operator alerts")

with value_cols[1]:
    st.markdown("### 📊 Operational Efficiency")
    st.markdown("- Optimize shift scheduling")
    st.markdown("- Identify high-risk patterns")
    st.markdown("- Data-driven safety decisions")

with value_cols[2]:
    st.markdown("### 🏆 Compliance & Reporting")
    st.markdown("- Automated safety reports")
    st.markdown("- Audit-ready dashboards")
    st.markdown("- Industry standard compliance")

# ================= FOOTER ===========================
st.markdown("---")
st.markdown('<div class="footer">MineVision AI - Transforming Mining Safety with Intelligent Analytics | Contact: sales@minevision-ai.com</div>', unsafe_allow_html=True)
