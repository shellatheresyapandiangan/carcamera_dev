import streamlit as st
import pandas as pd
import plotly.express as px

# =================== APP CONFIG =====================
st.set_page_config(
    page_title="Fatigue Safety Dashboard",
    page_icon="😴",
    layout="wide"
)

st.title("😴 Fatigue Monitoring Analytics")
st.write("Automated reporting for fatigue & distraction events in mining operations.")


# =================== LOAD DATA ======================
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/shellatheresyapandiangan/carcamera_dev/main/manual%20fatique.xlsx"

    # Read Excel from GitHub
    data = pd.read_excel(url, sheet_name=None, engine="openpyxl")

    # Merge all sheets if multiple
    df = pd.concat(data.values(), ignore_index=True) if isinstance(data, dict) else data

    # Normalize columns
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(" ", "_")
        .str.lower()
    )

    # Detect timestamp columns
    timestamp_cols = [col for col in df.columns if "gmt" in col or "time" in col or "date" in col]

    if len(timestamp_cols) >= 2:
        df["start"] = pd.to_datetime(df[timestamp_cols[0]], errors="coerce")
        df["end"] = pd.to_datetime(df[timestamp_cols[1]], errors="coerce")

    # Compute duration and hour
    df["duration_sec"] = (df["end"] - df["start"]).dt.total_seconds()
    df["hour"] = df["start"].dt.hour

    return df


# Load and show data
try:
    df = load_data()
    st.success("Data loaded successfully 🎉")
except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()

st.dataframe(df, use_container_width=True)



# =================== KPI METRICS =====================
st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Events", f"{len(df):,}")
col2.metric("Operators", df["operator_name"].nunique() if "operator_name" in df else "-")
col3.metric("Assets", df["asset_number"].nunique() if "asset_number" in df else "-")
col4.metric("Avg Event Duration", f"{round(df['duration_sec'].mean(),1)} sec")


# =================== CHARTS ==========================
st.subheader("📈 Fatigue Behaviour Trends")


if "hour" in df.columns:
    fig_hour = px.bar(
        df.groupby("hour").size().reset_index(name="events"),
        x="hour",
        y="events",
        title="⏰ Fatigue Alerts by Time of Day",
    )
    st.plotly_chart(fig_hour, use_container_width=True)


if "operator_name" in df.columns:
    fig_operator = px.bar(
        df["operator_name"].value_counts().reset_index(names=["operator", "alerts"]),
        x="operator",
        y="alerts",
        title="🏆 Top Operators with Most Fatigue Alerts"
    )
    st.plotly_chart(fig_operator, use_container_width=True)


if "alarm_type" in df.columns:
    fig_type = px.pie(
        df,
        names="alarm_type",
        title="🚨 Alert Type Distribution",
        hole=0.4
    )
    st.plotly_chart(fig_type, use_container_width=True)



# =================== AI INSIGHT ======================
st.subheader("🧠 Automated Safety Insight")

insight_list = []

# Peak fatigue hour
peak_hour = df["hour"].value_counts().idxmax()
insight_list.append(f"⏱ Peak fatigue occurs at **{peak_hour}:00**, likely during reduced alertness.")

# Worst operator
if "operator_name" in df.columns:
    worst = df["operator_name"].value_counts().idxmax()
    insight_list.append(f"⚠ Operator with highest event count: **{worst}**. Recommended coaching / supervision.")

# Duration warning
if df["duration_sec"].mean() > 8:
    insight_list.append("⏳ Average event duration is high, suggesting slow driver response time.")

for text in insight_list:
    st.write(f"- {text}")



# ================= FOOTER ===========================
st.markdown("---")
st.caption("📍 Fatigue Safety Automation System — Powered by Streamlit")

