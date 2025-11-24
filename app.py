import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json

# =================== CONFIG =====================
st.set_page_config(
    page_title="MineVision AI - Advanced Fatigue Analytics",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force light theme for entire app
st.markdown("""
<style>
    /* Force white background for entire Streamlit app */
    .stApp {
        background-color: white !important;
        color: #333333 !important;
    }
    
    /* Remove all background colors from Streamlit containers */
    .css-1d391kg, .css-1v3fvcr, .css-1l02z7j, .css-1n7v2ny, .css-145kmo2, .css-1y4p8pa {
        background-color: white !important;
        border: none !important;
    }
    
    /* Ensure text is readable */
    body, p, div, span, h1, h2, h3, h4, h5, h6 {
        color: #333333 !important;
    }
    
    /* Fix Plotly chart background */
    .plotly-graph-div {
        background-color: white !important;
    }
    
    /* Header styling - no background, clean professional look */
    .main-header {
        padding: 25px;
        margin-bottom: 25px;
        text-align: center;
        border-bottom: 2px solid #003366;
        color: #003366;
        font-weight: bold;
    }
    
    .main-header h1 {
        font-size: 2.5em;
        margin-bottom: 5px;
        color: #003366;
    }
    
    .main-header p {
        font-size: 1.2em;
        color: #666666;
        margin-top: 10px;
    }
    
    /* Metric card styling */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #003366;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e1e8f0;
    }
    
    /* Insight box styling */
    .insight-box {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #ff6b6b;
        margin: 15px 0;
        box-shadow: 0 4px 20px rgba(255, 107, 107, 0.1);
        border: 1px solid #ffe0e0;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 25px;
        color: #666666;
        font-size: 0.95em;
        background: white;
        border-top: 1px solid #e1e8f0;
        margin-top: 30px;
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        padding: 25px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.08);
        border: 1px solid #e1e8f0;
    }
    
    /* Subheader styling */
    .subheader-style {
        padding: 15px 20px;
        border-radius: 12px;
        margin: 20px 0 25px 0;
        border-left: 4px solid #003366;
        box-shadow: 0 4px 15px rgba(0, 51, 102, 0.1);
        border: 1px solid #e1e8f0;
        background: white;
    }
    
    .subheader-style h2 {
        color: #003366;
        margin: 0;
    }
    
    /* Insight card */
    .insight-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 5px solid #ff6b6b;
        box-shadow: 0 3px 15px rgba(255, 107, 107, 0.1);
        border: 1px solid #ffe0e0;
    }
    
    /* Metric container */
    .metric-container {
        background: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.08);
        border: 1px solid #e1e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Header - Professional, no background, no icons
st.markdown("""
<div class="main-header">
    <h1>MineVision AI - Advanced Fatigue Analytics</h1>
    <p>Proactive Safety Intelligence for Mining Operations</p>
</div>
""", unsafe_allow_html=True)

# # =================== CHAT AI SECTION =====================
# st.subheader("MineVision AI Assistant")

# # Initialize session state for chat
# if 'chat_history' not in st.session_state:
#     st.session_state.chat_history = []

# # Display chat history in a fancy box with white background
# st.markdown('<div class="chat-container">', unsafe_allow_html=True)
# for message in st.session_state.chat_history:
#     if message['role'] == 'user':
#         st.markdown(f'<div class="user-message">You: {message["content"]}</div>', unsafe_allow_html=True)
#     else:
#         st.markdown(f'<div class="ai-message">MineVision AI: {message["content"]}</div>', unsafe_allow_html=True)
# st.markdown('</div>', unsafe_allow_html=True)

# # Input for user question
# user_input = st.text_input("Ask a question about the fatigue data...", key="chat_input")

# def get_groq_response(prompt):
#     """Function to get response from Groq API"""
#     api_key = "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"  # Your provided token
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#         "Content-Type": "application/json"
#     }
    
#     # Construct the full prompt with context
#     full_prompt = f"Context: Mining fatigue data analysis dashboard. Question: {prompt}"
    
#     payload = {
#         "model": "llama3-70b-8192",  # Using a powerful model
#         "messages": [
#             {"role": "system", "content": "You are an expert in mining safety and fatigue risk management. Provide concise, accurate answers based on the provided mining fatigue data and general knowledge of mining operations."},
#             {"role": "user", "content": full_prompt}
#         ],
#         "temperature": 0.5,
#         "max_tokens": 500,
#         "top_p": 1,
#         "stop": None
#     }
    
#     try:
#         response = requests.post("https://api.groq.com/openai/v1/chat/completions  ", headers=headers, json=payload)
#         response.raise_for_status()
#         result = response.json()
#         return result['choices'][0]['message']['content'].strip()
#     except requests.exceptions.RequestException as e:
#         return f"Error calling Groq API: {str(e)}"
#     except KeyError:
#         return "Received unexpected response from Groq API."

# if st.button("Send", key="send_button"):
#     if user_input:
#         # Add user message to history
#         st.session_state.chat_history.append({"role": "user", "content": user_input})
        
#         # Get response from Groq API
#         response = get_groq_response(user_input)
        
#         # Add AI response to history
#         st.session_state.chat_history.append({"role": "assistant", "content": response})
        
#         # Rerun to update the chat display
#         st.rerun()


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
        df["month"] = df["start"].dt.month # Add month for filtering
        df["year"] = df["start"].dt.year # Add year for filtering

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

st.success("Data Loaded Successfully")

# =================== FILTERS (Sidebar) =====================
st.sidebar.header("Filters")

# Year Filter
if 'year' in df.columns:
    all_years = sorted(df['year'].dropna().unique())
    selected_years = st.sidebar.multiselect(
        "Select Year (Leave blank for All)",
        options=all_years,
        default=all_years  # Default to all if none selected
    )
    if selected_years:
        df = df[df['year'].isin(selected_years)]

# Month Filter
if 'month' in df.columns:
    all_months = sorted(df['month'].dropna().unique())
    selected_months = st.sidebar.multiselect(
        "Select Month (Leave blank for All)",
        options=all_months,
        default=all_months  # Default to all if none selected
    )
    if selected_months:
        df = df[df['month'].isin(selected_months)]

# Week Filter
if 'week' in df.columns:
    all_weeks = sorted(df['week'].dropna().unique())
    selected_weeks = st.sidebar.multiselect(
        "Select Week (Leave blank for All)",
        options=all_weeks,
        default=all_weeks  # Default to all if none selected
    )
    if selected_weeks:
        df = df[df['week'].isin(selected_weeks)]

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

# Operator Filter (with search functionality)
if col_operator:
    all_operators = sorted(df[col_operator].dropna().unique())
    # Use multiselect with search functionality
    selected_operators = st.sidebar.multiselect(
        f"Select {col_operator.replace('_', ' ').title()} (Leave blank for All)",
        options=all_operators,
        default=all_operators,  # Default to all if none selected
        format_func=lambda x: x  # Format function for better display
    )
    if selected_operators:
        df = df[df[col_operator].isin(selected_operators)]

# Shift Filter (with search functionality) - Ensure integers
if col_shift:
    all_shifts = sorted(df[col_shift].dropna().unique())
    # Use multiselect with search functionality
    selected_shifts = st.sidebar.multiselect(
        f"Select {col_shift.replace('_', ' ').title()} (Leave blank for All)",
        options=all_shifts,
        default=all_shifts,  # Default to all if none selected
    )
    if selected_shifts:
        df = df[df[col_shift].isin(selected_shifts)]

# Hour Range Filter
all_hours = sorted(df['hour'].dropna().unique())
if len(all_hours) > 0:
    hour_range = st.sidebar.slider(
        "Select Hour Range (Leave at full range for All)",
        min_value=int(min(all_hours)),
        max_value=int(max(all_hours)),
        value=(int(min(all_hours)), int(max(all_hours))),
        step=1
    )
    if hour_range != (int(min(all_hours)), int(max(all_hours))):
        df = df[(df['hour'] >= hour_range[0]) & (df['hour'] <= hour_range[1])]
else:
    # Handle case where there are no hours
    st.sidebar.text("No hour data available")
    hour_range = (0, 23)


# =================== FATIGUE RISK CATEGORIZATION =====================
st.markdown('<div class="subheader-style"><h2>Fatigue Risk Categorization</h2></div>', unsafe_allow_html=True)

# Define risk categories based on the provided matrix
if col_speed and "hour" in df.columns:
    # Create risk category column based on the matrix
    df['risk_category'] = df.apply(lambda row: 
        'Critical' if (row[col_speed] > df[col_speed].quantile(0.75) and row['hour'] in [2, 3, 4, 5]) else
        'High' if (row[col_speed] > df[col_speed].quantile(0.5) and row['hour'] in [2, 3, 4, 5]) else
        'Medium' if (row[col_speed] > df[col_speed].quantile(0.25) and row['hour'] in [2, 3, 4, 5]) else
        'Low' if (row[col_speed] <= df[col_speed].quantile(0.25) and row['hour'] not in [2, 3, 4, 5]) else
        'Medium', axis=1)  # Default to medium for other cases
    
    # Count alerts by risk category
    risk_counts = df['risk_category'].value_counts().reindex(['Critical', 'High', 'Medium', 'Low'])
    
    # Create a bar chart showing the distribution of risk categories
    fig_risk = px.bar(
        x=risk_counts.index,
        y=risk_counts.values,
        title="Fatigue Risk Categories Distribution",
        labels={'x': 'Risk Category', 'y': 'Number of Alerts'},
        color=risk_counts.index,
        color_discrete_map={'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'green'}
    )
    fig_risk.update_layout(
        xaxis_title="Risk Category",
        yaxis_title="Number of Alerts",
        height=400
    )
    # Add legend to explain each category
    fig_risk.update_layout(
        legend_title_text="Risk Level",
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    # Add annotations to explain what each risk level means
    for i, (cat, count) in enumerate(risk_counts.items()):
        if cat == 'Critical':
            fig_risk.add_annotation(
                x=cat,
                y=count + 1,
                text="High fatigue + high-speed haul road",
                showarrow=False,
                font=dict(size=10),
                bgcolor="red",
                opacity=0.8
            )
        elif cat == 'High':
            fig_risk.add_annotation(
                x=cat,
                y=count + 1,
                text="Moderate fatigue + decline haul road",
                showarrow=False,
                font=dict(size=10),
                bgcolor="orange",
                opacity=0.8
            )
        elif cat == 'Medium':
            fig_risk.add_annotation(
                x=cat,
                y=count + 1,
                text="High fatigue + low-risk task",
                showarrow=False,
                font=dict(size=10),
                bgcolor="yellow",
                opacity=0.8
            )
        elif cat == 'Low':
            fig_risk.add_annotation(
                x=cat,
                y=count + 1,
                text="Low fatigue + non-hazard task",
                showarrow=False,
                font=dict(size=10),
                bgcolor="green",
                opacity=0.8
            )
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_risk, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# =================== KPI METRICS =====================
st.markdown('<div class="subheader-style"><h2>Executive Safety Dashboard</h2></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Total Alerts", f"{len(df):,}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Operators", df[col_operator].nunique() if col_operator else "-")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Qty Equipment", df[col_asset].nunique() if col_asset else "-")  # Changed from "Assets" to "Qty Equipment"
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Avg Duration (sec)", round(df["duration_sec"].mean(),2) if "duration_sec" in df.columns else "N/A")
    st.markdown('</div>', unsafe_allow_html=True)


# =================== TREND ANALYTICS =====================
st.markdown('<div class="subheader-style"><h2>Fatigue Trend Analysis</h2></div>', unsafe_allow_html=True)

# Hourly
fig_hour = px.bar(
    df.groupby("hour").size().reset_index(name="alerts"),
    x="hour", y="alerts",
    title="Fatigue Alerts by Hour"
)
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig_hour, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Shift-Based
if col_shift:
    fig_shift = px.bar(
        df.groupby(col_shift).size().reset_index(name="alerts"),
        x=col_shift, y="alerts",
        title="Fatigue Distribution by Shift"
    )
    # Force the x-axis (shift) to be categorical to avoid decimal labels
    fig_shift.update_xaxes(type='category')
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_shift, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # hour inside shift heatmap
    heat_df = df.groupby([col_shift, "hour"]).size().reset_index(name="alerts")

    fig_heat = px.density_heatmap(
        heat_df,
        x="hour", y=col_shift, z="alerts",
        title="Heatmap Fatigue by Shift & Hour",
        color_continuous_scale="reds"
    )
    # Force the y-axis (shift) to be categorical to avoid decimal labels
    fig_heat.update_yaxes(type='category')
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_heat, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# Operator Ranking
if col_operator:
    operator_counts = df[col_operator].value_counts().reset_index()
    operator_counts.columns = ["operator", "alerts"]
    fig_operator = px.bar(
        operator_counts,
        x="operator", y="alerts",
        title="Top Fatigue Alerts by Operator"
    )
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_operator, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# =================== NEW CHARTS (Based on Mining Fatigue Factors) =====================
st.markdown('<div class="subheader-style"><h2>Advanced Mining Fatigue Analytics</h2></div>', unsafe_allow_html=True)

# 1. Day of Week Analysis (Workload Pattern)
if 'day_of_week' in df.columns:
    day_counts = df['day_of_week'].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    fig_day = px.bar(
        day_counts,
        x=day_counts.index, y=day_counts.values,
        title="Fatigue Alerts by Day of Week (Workload Pattern)"
    )
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_day, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 2. Fleet Type Analysis (Task & Workload)
if col_fleet_type:
    fleet_counts = df[col_fleet_type].value_counts().reset_index()
    fleet_counts.columns = [col_fleet_type, "alerts"]
    fig_fleet = px.bar(
        fleet_counts,
        x=col_fleet_type, y="alerts",
        title="Fatigue Alerts by Fleet Type (Task Complexity)"
    )
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_fleet, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 3. Speed vs Hour Analysis (Environmental Factors & Workload)
if col_speed and "hour" in df.columns:
    # Remove rows with NaN speed values for this analysis
    speed_df = df.dropna(subset=[col_speed])
    if not speed_df.empty:
        fig_speed_hour = px.scatter(
            speed_df,
            x="hour", y=col_speed,
            title="Speed vs Hour of Day (Fatigue Events) - Environmental Factor",
            hover_data=[col_operator, col_asset]
        )
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.plotly_chart(fig_speed_hour, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# 4. Duration vs Hour Analysis (Physiological Response)
if "duration_sec" in df.columns and "hour" in df.columns:
    fig_duration_hour = px.scatter(
        df,
        x="hour", y="duration_sec",
        title="Fatigue Event Duration vs Hour of Day (Physiological Response)",
        hover_data=[col_operator, col_asset]
    )
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_duration_hour, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 5. Operator vs Shift Analysis (Shift Pattern Risk)
if col_operator and col_shift:
    op_shift_counts = df.groupby([col_operator, col_shift]).size().reset_index(name="alerts")
    fig_op_shift = px.bar(
        op_shift_counts,
        x=col_operator, y="alerts", color=col_shift,
        title="Operator Fatigue Distribution by Shift (Shift Pattern Risk)"
    )
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_op_shift, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 6. Weekly Trend Analysis (Recovery Pattern) - With Color by Shift
if 'week' in df.columns and col_shift:
    # Create a new column for the legend
    df['shift_legend'] = df[col_shift].apply(lambda x: f"Shift {x}")
    
    # Group by week and shift
    weekly_shift_trend = df.groupby(['week', 'shift_legend']).size().reset_index(name='alerts')
    
    fig_weekly = px.line(
        weekly_shift_trend,
        x='week', y='alerts',
        color='shift_legend',
        title="Weekly Fatigue Trend by Shift (Recovery Pattern)",
        markers=True
    )
    # Customize colors for each shift
    if len(weekly_shift_trend['shift_legend'].unique()) >= 2:
        # Assign specific colors to shifts (e.g., Shift 1: blue, Shift 2: red)
        color_map = {}
        unique_shifts = sorted(weekly_shift_trend['shift_legend'].unique())
        for i, shift in enumerate(unique_shifts):
            if i == 0:
                color_map[shift] = 'blue'
            elif i == 1:
                color_map[shift] = 'red'
            else:
                color_map[shift] = f'hsl({i*60}, 70%, 50%)'  # Generate different colors for more than 2 shifts
        
        fig_weekly.update_traces(marker=dict(size=8))
        fig_weekly.update_layout(
            legend_title_text="Shift",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        # Apply custom colors
        for trace in fig_weekly.data:
            if trace.name in color_map:
                trace.line.color = color_map[trace.name]
                trace.marker.color = color_map[trace.name]
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_weekly, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 7. Speed Distribution Analysis (Task Complexity)
if col_speed:
    speed_df_clean = df.dropna(subset=[col_speed])
    if not speed_df_clean.empty:
        fig_speed_dist = px.histogram(
            speed_df_clean,
            x=col_speed,
            title="Speed Distribution (Task Complexity Indicator)",
            nbins=20
        )
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.plotly_chart(fig_speed_dist, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# =================== INSIGHTS BY ADVANCED ANALYTICS =====================
st.markdown('<div class="subheader-style"><h2>Insights by Advanced Analytics</h2></div>', unsafe_allow_html=True)

# 1. Critical Hour Analysis (2-5 AM)
critical_hours = [2, 3, 4, 5]
critical_alerts = df[df['hour'].isin(critical_hours)]
critical_pct = (len(critical_alerts) / len(df)) * 100 if len(df) > 0 else 0

st.markdown(f"### Critical Hour Risk (2-5 AM)")
# Use conditional formatting for background color
bg_color = "#ffcccc" if critical_pct > 50 else "#ffebcc" if critical_pct > 25 else "#ffffcc" if critical_pct > 10 else "#e6ffe6"
st.markdown(f'<div style="background-color: {bg_color}; padding: 15px; border-radius: 10px; border: 2px solid #ccc;">Critical Hour Alerts: {len(critical_alerts)} ({critical_pct:.1f}% of total alerts)</div>', unsafe_allow_html=True)
if critical_pct > 10:  # If more than 10% of alerts happen in critical hours
    st.warning(f"High risk: {critical_pct:.1f}% of fatigue alerts occur during critical hours (2-5 AM). This is a known circadian dip period.")
else:
    st.info(f"{critical_pct:.1f}% of alerts occur during critical hours. This is within acceptable range.")

# 2. High-Speed Fatigue Analysis (Environmental Risk)
if col_speed:
    high_speed_threshold = df[col_speed].quantile(0.75)  # Top 25% of speeds
    high_speed_fatigue = df[df[col_speed] >= high_speed_threshold]
    high_speed_pct = (len(high_speed_fatigue) / len(df)) * 100 if len(df) > 0 else 0
    
    st.markdown(f"### High-Speed Fatigue Risk (Speed > {high_speed_threshold:.0f} km/h)")
    st.metric("High-Speed Fatigue Events", f"{len(high_speed_fatigue)}", f"{high_speed_pct:.1f}% of total alerts")
    if high_speed_pct > 20:  # If more than 20% of alerts happen at high speed
        st.warning(f"High risk: {high_speed_pct:.1f}% of fatigue alerts occur at high speeds. This increases accident severity potential.")
    else:
        st.info(f"{high_speed_pct:.1f}% of alerts occur at high speeds. This is within acceptable range.")

# 3. Shift Pattern Analysis
if col_shift:
    shift_counts = df[col_shift].value_counts()
    shift_alerts_by_hour = df.groupby([col_shift, 'hour']).size().reset_index(name='alerts')
    
    st.markdown(f"### Shift Pattern Risk")
    for shift_val in shift_counts.index:
        shift_pct = (shift_counts[shift_val] / len(df)) * 100
        st.metric(f"Shift {shift_val} Alerts", f"{shift_counts[shift_val]}", f"{shift_pct:.1f}% of total alerts")
        if shift_pct > 50:  # If one shift has more than 50% of alerts
            st.warning(f"Shift {shift_val} has disproportionately high alerts ({shift_pct:.1f}%). Review shift scheduling and workload.")
        else:
            st.info(f"Shift {shift_val} alert distribution is acceptable ({shift_pct:.1f}%).")

# 4. Operator Risk Profiling
if col_operator:
    operator_alerts = df[col_operator].value_counts()
    top_risk_operators = operator_alerts.head(5)  # Top 5 operators by alerts
    
    st.markdown(f"### High-Risk Operator Identification")
    for op_name, count in top_risk_operators.items():
        op_pct = (count / len(df)) * 100
        st.metric(f"Operator: {op_name}", f"{count} alerts", f"{op_pct:.1f}% of total alerts")
        if op_pct > 5:  # If an operator has more than 5% of all alerts
            st.warning(f"Operator {op_name} has high fatigue risk ({op_pct:.1f}% of alerts). Consider coaching or rest plan.")
        else:
            st.info(f"Operator {op_name} fatigue risk is within acceptable range ({op_pct:.1f}%).")


# # =================== FATIGUE RISK MATRIX =====================
# # Moved to sidebar
# with st.sidebar:
#     st.subheader("Fatigue Risk Matrix")
    
#     risk_matrix_data = [
#         ["High fatigue + high-speed haul road", "Potential fatality", "Critical"],
#         ["Moderate fatigue + decline haul road", "Serious injury", "High"],
#         ["High fatigue + low-risk task", "Minor injury", "Medium"],
#         ["Low fatigue + non-hazard task", "No injury", "Low"]
#     ]
    
#     risk_df = pd.DataFrame(risk_matrix_data, columns=["Likelihood (Fatigue Level)", "Severity (Hazard Impact)", "Risk Tier"])
    
#     # Display risk matrix as a styled table
#     html_string = '<table class="risk-matrix"><thead><tr><th>Likelihood (Fatigue Level)</th><th>Severity (Hazard Impact)</th><th>Risk Tier</th></tr></thead><tbody>'
#     for _, row in risk_df.iterrows():
#         risk_class = row["Risk Tier"].lower()
#         html_string += f'<tr class="{risk_class}"><td>{row["Likelihood (Fatigue Level)"]}</td><td>{row["Severity (Hazard Impact)"]}</td><td>{row["Risk Tier"]}</td></tr>'
#     html_string += '</tbody></table>'
    
#     st.markdown(html_string, unsafe_allow_html=True)


# =================== AI INSIGHT ENGINE =====================
st.markdown('<div class="subheader-style"><h2>Automated Insight Summary</h2></div>', unsafe_allow_html=True)

# Create a more elegant summary
insights = []

# Peak hour
if "hour" in df.columns and not df.empty:
    peak_hour = df["hour"].value_counts().idxmax()
    critical_hours = [2, 3, 4, 5]
    if peak_hour in critical_hours:
        insights.append(f"Most fatigue risk occurs at **{peak_hour}:00** — during critical circadian low period (2-5 AM). Consider enhanced monitoring.")
    else:
        insights.append(f"Most fatigue risk occurs at **{peak_hour}:00** — likely due to circadian drop.")

# Risk shift
if col_shift and not df.empty:
    worst_shift = df[col_shift].value_counts().idxmax()
    insights.append(f"Highest fatigue recorded in **Shift {worst_shift}** — review scheduling & workload.")

# Worst operator
if col_operator and not df.empty:
    worst_operator = df[col_operator].value_counts().idxmax()
    insights.append(f"Operator at highest risk: **{worst_operator}** — suggested coaching or rest plan.")

# Duration risk
if "duration_sec" in df.columns and not df.empty:
    avg_duration = df["duration_sec"].mean()
    if not pd.isna(avg_duration) and avg_duration > 10:
        insights.append("Long fatigue event duration suggests slow response — improve alerting training.")

# Critical hour insight
if "hour" in df.columns and not df.empty:
    critical_alerts = df[df['hour'].isin([2, 3, 4, 5])]
    if len(critical_alerts) > 0:
        critical_pct = (len(critical_alerts) / len(df)) * 100
        if critical_pct > 15:
            insights.append(f"**CRITICAL HOUR RISK**: {critical_pct:.1f}% of alerts occur during circadian low (2-5 AM). Consider enhanced monitoring during this period.")

# High-speed insight
if col_speed and not df.empty:
    high_speed_fatigue = df[df[col_speed] >= df[col_speed].quantile(0.75)] if not df[col_speed].dropna().empty else pd.DataFrame()
    if len(high_speed_fatigue) > 0:
        high_speed_pct = (len(high_speed_fatigue) / len(df)) * 100
        if high_speed_pct > 20:
            insights.append(f"**HIGH-SPEED RISK**: {high_speed_pct:.1f}% of fatigue events occur at high speeds, increasing accident severity potential.")

# Output insights in an elegant format
for i in insights:
    st.markdown(f'<div class="insight-card">{i}</div>', unsafe_allow_html=True)


# ================= FOOTER ===========================
st.markdown("---")
st.markdown('<div class="footer">MineVision AI - Transforming Mining Safety with Intelligent Analytics | Contact: sales@minevision-ai.com</div>', unsafe_allow_html=True)
