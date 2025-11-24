import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Fatigue Safety Dashboard", layout="wide", page_icon="😴")

st.title("Fatigue Monitoring & Safety Operator Analytics")

@st.cache_data
def load_data():
    path = "/mnt/data/manual fatique.xlsx"
    data = pd.read_excel(path, sheet_name=None, engine="openpyxl")
    df = pd.concat(data.values(), ignore_index=True) if isinstance(data, dict) else data

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(" ", "_")
        .str.lower()
    )

    # detect key columns
    col_operator = next((c for c in df.columns if "operator" in c or "driver" in c), None)
    col_shift = next((c for c in df.columns if "shift" in c), None)

    # timestamp
    timestamp_cols = [c for c in df.columns if "gmt" in c or "time" in c or "date" in c]
    if len(timestamp_cols) >= 2:
        df["start"] = pd.to_datetime(df[timestamp_cols[0]], errors="coerce")
        df["end"] = pd.to_datetime(df[timestamp_cols[1]], errors="coerce")
    df["duration_sec"] = (df["end"] - df["start"]).dt.total_seconds()
    df["hour"] = df["start"].dt.hour

    # Clean shift to 1 or 2
    if col_shift:
        df[col_shift] = df[col_shift].astype(str).str.extract(r"(\d+)").astype(float).astype(int)

    return df, col_operator, col_shift

df, col_operator, col_shift = load_data()

if col_operator is None or col_shift is None:
    st.error("Kolom operator atau shift tidak ditemukan. Periksa dataset Anda.")
    st.stop()

st.success("Data loaded successfully!")
st.dataframe(df.head(), use_container_width=True)

# KPIs
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Events", f"{len(df):,}")
col2.metric("Unique Operators", df[col_operator].nunique())
col3.metric("Avg Duration (s)", round(df["duration_sec"].mean(), 1))
col4.metric("Shifts In Dataset", df[col_shift].nunique())

# Trend by hour
st.subheader("Trend by Hour")
fig_hour = px.bar(
    df.groupby("hour").size().reset_index(name="alerts"),
    x="hour", y="alerts",
    title="Alerts by Hour of Day"
)
st.plotly_chart(fig_hour, use_container_width=True)

# Trend by shift
st.subheader("Distribution by Shift")
fig_shift = px.bar(
    df.groupby(col_shift).size().reset_index(name="alerts"),
    x=col_shift, y="alerts",
    title="Alerts by Shift"
)
st.plotly_chart(fig_shift, use_container_width=True)

# Heatmap hour vs shift
st.subheader("Heatmap: Shift vs Hour")
heat_df = df.groupby([col_shift, "hour"]).size().reset_index(name="alerts")
fig_heat = px.density_heatmap(
    heat_df, x="hour", y=col_shift, z="alerts",
    title="Fatigue Alerts Heatmap (Hour vs Shift)",
    color_continuous_scale="reds"
)
st.plotly_chart(fig_heat, use_container_width=True)

# Operator ranking
st.subheader("Operator Safety Performance")
op_counts = df[col_operator].value_counts().reset_index()
op_counts.columns = ["operator", "alerts"]
fig_op = px.bar(
    op_counts.head(10), x="operator", y="alerts",
    title="Top 10 Operators – Most Alerts"
)
st.plotly_chart(fig_op, use_container_width=True)
st.table(op_counts.head(10))

# Tambah analisa operator “safe” – operator dengan alerts rendah
safe_threshold = op_counts["alerts"].quantile(0.25)
safe_ops = op_counts[op_counts["alerts"] <= safe_threshold]
st.subheader("Operators with Low Alert Count (Safer)")
st.table(safe_ops.head(10))

# Insight text
st.subheader("Automated Insights")
insights = []
peak_hour = df["hour"].value_counts().idxmax()
insights.append(f"Peak alert hour: **{peak_hour}:00**.")
worst_shift = df[col_shift].value_counts().idxmax()
insights.append(f"Higher alerts during Shift {worst_shift}, review staffing & rest breaks.")
worst_op = op_counts.iloc[0]["operator"]
insights.append(f"Operator most at risk: **{worst_op}** — recommend focused safety coaching.")
for i in insights:
    st.write("- " + i)

st.markdown("---")
st.caption("Fatigue & Safety Operator Monitoring Dashboard")
