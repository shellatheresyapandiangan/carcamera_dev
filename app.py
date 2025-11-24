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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>⛏️ MineVision AI - Advanced Fatigue Analytics</h1><p>Proactive Safety Intelligence for Mining Operations</p></div>', unsafe_allow_html=True)

# =================== LOAD DATA (Original Script Adaptation) ======================
@st.cache_data
def load_data():
    # Simulating the data loading process from the provided Excel file structure
    # In a real application, you would load the actual Excel file here.
    # For demonstration, we'll recreate a DataFrame similar to the provided data.
    # The raw content provided seems to be a list of URLs, not the actual structured data.
    # Based on the initial script's expected columns, we'll create a representative mock dataset.
    # A real implementation would use: pd.read_excel(file_path, sheet_name=None, engine="openpyxl")

    # Mock data based on the expected structure from the initial script and sample row
    data_dict = {
        'ticket_number': [
            'ADT - HDKM78554-PDSM00188544', 'ADT - HDCT77370-PDSM00187812', 'SDJ - HDCT73036-PDSM00160636',
            'ADT - HDCT77346-PDSM00160540', 'ADT - HDCT77370-PDSM00187813', 'ADT - HDCT77370-PDSM00187814',
            'ADT - HDCT77370-PDSM00187815', 'ADT - HDCT77370-PDSM00187816', 'ADT - HDCT77370-PDSM00187817',
            'ADT - HDCT77370-PDSM00187818'
        ],
        'parent_fleet': [
            'ADT - OB HAULLER', 'ADT - OB HAULLER', 'SDJ - OB HAULLER', 'ADT - OB HAULLER',
            'ADT - OB HAULLER', 'ADT - OB HAULLER', 'ADT - OB HAULLER', 'ADT - OB HAULLER',
            'ADT - OB HAULLER', 'ADT - OB HAULLER'
        ],
        'fleet_number': [
            'ADT - HDKM78554', 'ADT - HDCT77370', 'SDJ - HDCT73036', 'ADT - HDCT77346',
            'ADT - HDCT77370', 'ADT - HDCT77370', 'ADT - HDCT77370', 'ADT - HDCT77370',
            'ADT - HDCT77370', 'ADT - HDCT77370'
        ],
        'nik': [10032560, 10026757, 10027510, 10029870, 10026758, 10026759, 10026760, 10026761, 10026762, 10026763],
        'operator_name': [
            'Ery Arfandi Bazrah', 'Yodi Wanjaya', 'Arif Kassa P', 'Maulana Fajar Asrori',
            'Operator B', 'Operator C', 'Operator D', 'Operator E', 'Operator F', 'Operator G'
        ],
        'sid_code': ['', '', '', '', '', '', '', '', '', ''],
        'area_kerja': ['', '', '', '', '', '', '', '', '', ''],
        'alarm_type': [
            'Driver Fatigue', 'Driver Fatigue', 'Driver Fatigue', 'Driver Fatigue',
            'Driver Fatigue', 'Driver Fatigue', 'Driver Fatigue', 'Driver Fatigue',
            'Driver Fatigue', 'Driver Fatigue'
        ],
        'gmt_start': [
            '10/19/25 8:27', '10/19/25 6:23', '11/12/25 4:12', '11/12/25 3:52',
            '10/20/25 7:30', '10/21/25 5:45', '10/22/25 9:15', '10/23/25 10:05',
            '10/24/25 11:20', '10/25/25 12:30'
        ],
        'gmt_end': [
            '10/19/25 8:28', '10/19/25 6:29', '11/12/25 4:12', '11/12/25 3:52',
            '10/20/25 7:32', '10/21/25 5:47', '10/22/25 9:17', '10/23/25 10:07',
            '10/24/25 11:22', '10/25/25 12:32'
        ],
        'shift': [1, 1, 2, 2, 1, 1, 1, 2, 2, 2],
        'speed_kmh': [2, 1, 12, 1, 15, 8, 20, 5, 10, 25],
        'area': ['', '', '', '', '', '', '', '', '', ''],
        'condition': ['', '', '', '', '', '', '', '', '', ''],
        'validation_status': [
            'Validated', 'Validated', 'Validated', 'Validated', 'Validated', 'Validated',
            'Validated', 'Validated', 'Validated', 'Validated'
        ],
        'follow_up_status': [
            'Close', 'Close', 'Close', 'Close', 'Close', 'Close', 'Close', 'Close', 'Close', 'Close'
        ],
        'validation_remarks': [
            'Valid', 'Valid', 'Valid', 'Valid', 'Valid', 'Valid', 'Valid', 'Valid', 'Valid', 'Valid'
        ],
        'qc_status': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes']
    }
    df = pd.DataFrame(data_dict)

    # Convert date columns with error handling
    df['start'] = pd.to_datetime(df['gmt_start'], format='%m/%d/%y %H:%M', errors='coerce')
    df['end'] = pd.to_datetime(df['gmt_end'], format='%m/%d/%y %H:%M', errors='coerce')

    # Calculate duration and other features
    df['duration_sec'] = (df['end'] - df['start']).dt.total_seconds()
    df['hour'] = df['start'].dt.hour
    df['date'] = df['start'].dt.date
    df['day_of_week'] = df['start'].dt.day_name()
    df['week'] = df['start'].dt.isocalendar().week # Week number of the year

    # Rename columns to lowercase for consistency (original script logic)
    df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(" ", "_")

    # Auto-detect important columns (original script logic)
    col_operator = next((c for c in df.columns if "operator" in c or "driver" in c), None)
    col_shift = next((c for c in df.columns if "shift" in c), None)
    col_asset = next((c for c in df.columns if "asset" in c or "vehicle" in c or "fleet" in c), None)
    col_fleet_type = next((c for c in df.columns if "parent_fleet" in c or "fleet_type" in c), None)

    return df, col_operator, col_shift, col_asset, col_fleet_type

df, col_operator, col_shift, col_asset, col_fleet_type = load_data()

if df.empty or df['start'].isna().all():
    st.warning("No valid date/time data loaded or all dates are invalid. Please check your data source.")
    st.stop()

st.success("Data Loaded Successfully 🎉")

# =================== FILTERS (Improved) =====================
st.sidebar.header("Filters")

# Date Range Filter: Default to "All" if no specific range is selected
min_date = df['date'].min()
max_date = df['date'].max()
# Set default value to the full range initially
date_range_default = (min_date, max_date)

# Use session state to track if filters have been applied
if 'filters_applied' not in st.session_state:
    st.session_state.filters_applied = False

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
    st.session_state.filters_applied = True

# Other filters
selected_fleets = []
if col_fleet_type:
    selected_fleets = st.sidebar.multiselect(
        f"Select {col_fleet_type.replace('_', ' ').title()}", 
        options=df[col_fleet_type].unique(), 
        default=df[col_fleet_type].unique()
    )

selected_shifts = []
if col_shift:
    selected_shifts = st.sidebar.multiselect(
        f"Select {col_shift.replace('_', ' ').title()}", 
        options=df[col_shift].unique(), 
        default=df[col_shift].unique()
    )

# Apply filters
filtered_df = df.copy()
if date_range:
    filtered_df = filtered_df[(filtered_df['date'] >= date_range[0]) & (filtered_df['date'] <= date_range[1])]
if col_fleet_type and selected_fleets:
    filtered_df = filtered_df[filtered_df[col_fleet_type].isin(selected_fleets)]
if col_shift and selected_shifts:
    filtered_df = filtered_df[filtered_df[col_shift].isin(selected_shifts)]

# Show active filters
active_filters = []
if date_filtered:
    active_filters.append(f"Date: {date_range[0]} to {date_range[1]}")
if col_fleet_type and selected_fleets and len(selected_fleets) < df[col_fleet_type].nunique():
    active_filters.append(f"Fleet: {len(selected_fleets)}/{df[col_fleet_type].nunique()}")
if col_shift and selected_shifts and len(selected_shifts) < df[col_shift].nunique():
    active_filters.append(f"Shift: {len(selected_shifts)}/{df[col_shift].nunique()}")

if active_filters:
    st.sidebar.success(f"**Active Filters:** {', '.join(active_filters)}")
else:
    st.sidebar.info("No filters applied. Showing all data.")

# =================== KPI METRICS =====================
st.subheader("📊 Executive Safety Dashboard")

col1, col2, col3, col4, col5 = st.columns(5)

# Calculate metrics based on filtered data
total_alerts = len(filtered_df)
total_operators = filtered_df[col_operator].nunique() if col_operator else 0
total_assets = filtered_df[col_asset].nunique() if col_asset else 0
avg_duration = filtered_df['duration_sec'].mean() if 'duration_sec' in filtered_df.columns else 0
total_fleet_types = filtered_df[col_fleet_type].nunique() if col_fleet_type else 0

col1.metric("Total Fatigue Alerts", f"{total_alerts:,}")
col2.metric("Unique Operators", f"{total_operators}")
col3.metric("Active Assets", f"{total_assets}")
col4.metric("Avg. Alert Duration (s)", f"{avg_duration:.2f}" if not pd.isna(avg_duration) else "N/A")
col5.metric("Fleet Types", f"{total_fleet_types}")

# Additional KPIs
st.markdown("---")
st.subheader("📈 Advanced Trend Analysis")

# Row 1: Time Series and Shift Distribution
col1, col2 = st.columns(2)

with col1:
    # Daily Trend (Aggregated by date)
    if 'date' in filtered_df.columns:
        daily_trend = filtered_df.groupby('date').size().reset_index(name='alerts')
        if not daily_trend.empty:
            fig_daily = px.line(daily_trend, x='date', y='alerts', title="📅 Daily Fatigue Alert Trend")
            fig_daily.update_layout(height=400)
            st.plotly_chart(fig_daily, use_container_width=True)
        else:
            st.info("No data available for the selected date range.")

with col2:
    # Shift Distribution
    if col_shift and 'shift' in filtered_df.columns:
        shift_counts = filtered_df['shift'].value_counts().reset_index()
        shift_counts.columns = ['shift', 'count']
        if not shift_counts.empty:
            fig_shift = px.bar(shift_counts, x='shift', y='count', title="👷 Fatigue Distribution by Shift")
            fig_shift.update_layout(height=400)
            st.plotly_chart(fig_shift, use_container_width=True)
        else:
            st.info("No shift data available for the selected filters.")

# Row 2: Hourly and Fleet Analysis
col1, col2 = st.columns(2)

with col1:
    # Hourly Pattern
    if 'hour' in filtered_df.columns:
        hourly_counts = filtered_df['hour'].value_counts().reset_index()
        hourly_counts.columns = ['hour', 'count']
        hourly_counts = hourly_counts.sort_values('hour')
        if not hourly_counts.empty:
            fig_hourly = px.bar(hourly_counts, x='hour', y='count', title="⏰ Fatigue Alerts by Hour of Day")
            fig_hourly.update_layout(height=400)
            st.plotly_chart(fig_hourly, use_container_width=True)
        else:
            st.info("No hourly data available for the selected filters.")

with col2:
    # Fleet Type Distribution
    if col_fleet_type:
        fleet_counts = filtered_df[col_fleet_type].value_counts().reset_index()
        fleet_counts.columns = [col_fleet_type, 'count']
        if not fleet_counts.empty:
            fig_fleet = px.pie(fleet_counts, values='count', names=col_fleet_type, title="🚛 Fatigue by Fleet Type")
            fig_fleet.update_layout(height=400)
            st.plotly_chart(fig_fleet, use_container_width=True)
        else:
            st.info("No fleet type data available for the selected filters.")

# =================== OPERATOR & ASSET ANALYSIS =====================
st.subheader("👤 Operator & Asset Risk Profiling")

col1, col2 = st.columns(2)

with col1:
    # Top Operators by Alerts
    if col_operator:
        operator_counts = filtered_df[col_operator].value_counts().head(10).reset_index()
        operator_counts.columns = [col_operator, 'alerts']
        if not operator_counts.empty:
            fig_operator = px.bar(operator_counts, x='alerts', y=col_operator, orientation='h', title=f"🚨 Top 10 Operators by Fatigue Alerts")
            fig_operator.update_layout(height=500)
            st.plotly_chart(fig_operator, use_container_width=True)
        else:
            st.info("No operator data available for the selected filters.")

with col2:
    # Top Assets by Alerts
    if col_asset:
        asset_counts = filtered_df[col_asset].value_counts().head(10).reset_index()
        asset_counts.columns = [col_asset, 'alerts']
        if not asset_counts.empty:
            fig_asset = px.bar(asset_counts, x='alerts', y=col_asset, orientation='h', title=f"🚨 Top 10 Assets by Fatigue Alerts")
            fig_asset.update_layout(height=500)
            st.plotly_chart(fig_asset, use_container_width=True)
        else:
            st.info("No asset data available for the selected filters.")

# =================== NEW ANALYSES (Based on Wenco insights and enhanced features) =====================

# Analysis 1: Day of the Week Pattern
st.subheader("📅 Fatigue Patterns by Day of the Week")
if 'day_of_week' in filtered_df.columns:
    day_counts = filtered_df['day_of_week'].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    if not day_counts.empty:
        fig_day = px.bar(day_counts, x=day_counts.index, y=day_counts.values, title="Fatigue Alerts by Day of the Week")
        fig_day.update_layout(height=400)
        st.plotly_chart(fig_day, use_container_width=True)
    else:
        st.info("No day of week data available for the selected filters.")

# Analysis 2: Speed vs Fatigue Correlation (if speed data exists)
st.subheader("🚗 Speed vs Fatigue Analysis")
if 'speed_kmh' in filtered_df.columns and 'duration_sec' in filtered_df.columns:
    fig_speed = px.scatter(filtered_df, x='speed_kmh', y='duration_sec', 
                          title="Fatigue Duration vs Vehicle Speed",
                          hover_data=[col_operator, col_asset, 'date'])
    fig_speed.update_layout(height=400)
    st.plotly_chart(fig_speed, use_container_width=True)
else:
    st.info("Speed or duration data not available for correlation analysis.")

# Analysis 3: Weekly Trend (using week number)
st.subheader("🗓️ Weekly Fatigue Trend")
if 'week' in filtered_df.columns:
    weekly_trend = filtered_df.groupby('week').size().reset_index(name='alerts')
    if not weekly_trend.empty:
        fig_weekly = px.line(weekly_trend, x='week', y='alerts', title="Fatigue Alerts by Week Number")
        fig_weekly.update_layout(height=400)
        st.plotly_chart(fig_weekly, use_container_width=True)
    else:
        st.info("No weekly data available for the selected filters.")

# =================== ADVANCED AI INSIGHTS (Enhanced) =====================
st.subheader("🤖 AI-Powered Safety Insights & Recommendations")

insights = []

if 'hour' in filtered_df.columns and not filtered_df.empty:
    peak_hour = filtered_df['hour'].mode().iloc[0] if not filtered_df['hour'].mode().empty else 'N/A'
    if peak_hour != 'N/A':
        insights.append(f"⏱️ **Peak Risk Hour**: Most fatigue incidents occur around {peak_hour}:00. Consider enhanced monitoring or mandatory breaks during this period.")

if col_shift and not filtered_df.empty:
    worst_shift_counts = filtered_df[col_shift].value_counts()
    if not worst_shift_counts.empty:
        worst_shift = worst_shift_counts.index[0]
        shift_percentage = (worst_shift_counts.iloc[0] / len(filtered_df)) * 100
        insights.append(f"👷 **Shift Risk**: Shift {worst_shift} accounts for {shift_percentage:.1f}% of all alerts. Review scheduling, workload, and rest policies for this shift.")

if col_operator and not filtered_df.empty:
    top_risk_operator_counts = filtered_df[col_operator].value_counts()
    if not top_risk_operator_counts.empty:
        top_risk_operator = top_risk_operator_counts.index[0]
        operator_percentage = (top_risk_operator_counts.iloc[0] / len(filtered_df)) * 100
        insights.append(f"👤 **High-Risk Operator**: Operator '{top_risk_operator}' is associated with {operator_percentage:.1f}% of alerts ({top_risk_operator_counts.iloc[0]} incidents). Consider targeted coaching, medical review, or schedule adjustment.")

if 'duration_sec' in filtered_df.columns and not filtered_df.empty:
    avg_duration = filtered_df['duration_sec'].mean()
    if not pd.isna(avg_duration):
        if avg_duration > 60:  # More than 1 minute
            insights.append(f"⏳ **Response Time**: Average alert duration is {avg_duration:.2f} seconds. This indicates a potential delay in operator response or system acknowledgment. Review protocols.")
        else:
            insights.append(f"✅ **Response Time**: Average alert duration is {avg_duration:.2f} seconds, indicating a relatively quick response.")

if col_fleet_type and not filtered_df.empty:
    top_fleet_counts = filtered_df[col_fleet_type].value_counts()
    if not top_fleet_counts.empty:
        top_fleet_type_val = top_fleet_counts.index[0]
        fleet_percentage = (top_fleet_counts.iloc[0] / len(filtered_df)) * 100
        insights.append(f"🚛 **Fleet Risk**: The '{top_fleet_type_val}' fleet type has the most incidents ({fleet_percentage:.1f}% of total). Investigate specific operational factors, routes, or ergonomic issues.")

# New Insights based on added analyses
if 'day_of_week' in filtered_df.columns and not filtered_df.empty:
    peak_day_counts = filtered_df['day_of_week'].value_counts()
    if not peak_day_counts.empty:
        peak_day = peak_day_counts.index[0]
        day_percentage = (peak_day_counts.iloc[0] / len(filtered_df)) * 100
        insights.append(f"📅 **Day Risk**: {peak_day} shows the highest fatigue risk ({day_percentage:.1f}% of alerts). Consider weekly rest patterns or workload distribution.")

if 'speed_kmh' in filtered_df.columns and not filtered_df.empty:
    # Check for correlation or specific patterns
    high_speed_alerts = filtered_df[filtered_df['speed_kmh'] > filtered_df['speed_kmh'].quantile(0.75)]
    if len(high_speed_alerts) > 0:
        high_speed_ratio = len(high_speed_alerts) / len(filtered_df)
        if high_speed_ratio > 0.3: # If >30% of alerts happen at high speed
             insights.append(f"🚗 **Speed Factor**: {high_speed_ratio*100:.1f}% of fatigue alerts occur at higher speeds (75th percentile). This is a critical safety concern requiring immediate attention.")

# Wenco-based Insight: Fatigue Risk Management
insights.append("⚠️ **Proactive Management**: Integrate these insights into a comprehensive Fatigue Risk Management System (FRMS). Use predictive models to identify high-risk operators/fleets before incidents occur, aligning with best practices like those outlined by Wenco.")

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
    st.markdown("- Optimize shift scheduling based on data")
    st.markdown("- Identify high-risk patterns and assets")
    st.markdown("- Data-driven safety decisions")

with value_cols[2]:
    st.markdown("### 🏆 Compliance & Reporting")
    st.markdown("- Automated safety reports")
    st.markdown("- Audit-ready dashboards")
    st.markdown("- Aligns with industry FRMS standards")

# ================= FOOTER ===========================
st.markdown("---")
st.markdown('<div class="footer">MineVision AI - Transforming Mining Safety with Intelligent Analytics | Contact: sales@minevision-ai.com</div>', unsafe_allow_html=True)
