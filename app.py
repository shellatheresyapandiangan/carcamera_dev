import streamlit as st
import pandas as pd
import plotly.express as px

# =================== CONFIG =====================
st.set_page_config(
    page_title="Fatigue Safety Dashboard",
    page_icon="😴",
    layout="wide"
)

st.title("😴 Fatigue Monitoring Intelligence Dashboard")


# =================== LOAD DATA ======================
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/shellatheresyapandiangan/carcamera_dev/main/manual%20fatique.xlsx"

    data = pd.read_excel(url, sheet_name=None, engine="openpyxl")
    df = pd.concat(data.values(), ignore_index=True) if isinstance(data, dict) else data

    df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(" ", "_")

    # auto detect important columns
    col_operator = next((c for c in df.columns if "operator" in c or "driver" in c), None)
    col_shift = next((c for c in df.columns if "shift" in c), None)
    col_asset = next((c for c in df.columns if "asset" in c or "vehicle" in c or "fleet" in c), None)

    # detect timestamps
    timestamp_cols = [c for c in df.columns if "gmt" in c or "time" in c or "date" in c]

    if len(timestamp_cols) >= 2:
        df["start"] = pd.to_datetime(df[timestamp_cols[0]], errors="coerce")
        df["end"] = pd.to_datetime(df[timestamp_cols[1]], errors="coerce")

    df["duration_sec"] = (df["end"] - df["start"]).dt.total_seconds()
    df["hour"] = df["start"].dt.hour

    return df, col_operator, col_shift, col_asset


df, col_operator, col_shift, col_asset = load_data()

st.success("Data Loaded Successfully 🎉")

st.dataframe(df, use_container_width=True)

# =================== KPI METRICS =====================
st.subheader("📌 Key Safety Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Alerts", f"{len(df):,}")
col2.metric("Operators", df[col_operator].nunique() if col_operator else "-")
col3.metric("Assets", df[col_asset].nunique() if col_asset else "-")
col4.metric("Avg Duration (sec)", round(df["duration_sec"].mean(),2))


# =================== TREND ANALYTICS =====================
st.subheader("📈 Fatigue Trend Analysis")

# Hourly
fig_hour = px.bar(
    df.groupby("hour").size().reset_index(name="alerts"),
    x="hour", y="alerts",
    title="⏰ Fatigue Alerts by Hour"
)
st.plotly_chart(fig_hour, use_container_width=True)

# Shift-Based
if col_shift:
    fig_shift = px.bar(
        df.groupby(col_shift).size().reset_index(name="alerts"),
        x=col_shift, y="alerts",
        title="👷 Fatigue Distribution by Shift"
    )
    st.plotly_chart(fig_shift, use_container_width=True)

    # hour inside shift heatmap
    heat_df = df.groupby([col_shift, "hour"]).size().reset_index(name="alerts")

    fig_heat = px.density_heatmap(
        heat_df,
        x="hour", y=col_shift, z="alerts",
        title="🔥 Heatmap Fatigue by Shift & Hour",
        color_continuous_scale="reds"
    )
    st.plotly_chart(fig_heat, use_container_width=True)


# Operator Ranking
if col_operator:
    fig_operator = px.bar(
        df[col_operator].value_counts().reset_index(names=["operator", "alerts"]),
        x="operator", y="alerts",
        title="🏆 Top Fatigue Alerts by Operator"
    )
    st.plotly_chart(fig_operator, use_container_width=True)


# =================== AI INSIGHT ENGINE =====================
st.subheader("🧠 Automated Insight Summary")

insights = []

# Peak hour
peak_hour = df["hour"].value_counts().idxmax()
insights.append(f"⏱ Most fatigue risk occurs at **{peak_hour}:00** — likely due to circadian drop.")

# Risk shift
if col_shift:
    worst_shift = df[col_shift].value_counts().idxmax()
    insights.append(f"👷 Highest fatigue recorded in **Shift {worst_shift}** — review scheduling & workload.")

# Worst operator
if col_operator:
    worst_operator = df[col_operator].value_counts().idxmax()
    insights.append(f"⚠ Operator at highest risk: **{worst_operator}** — suggested coaching or rest plan.")

# Duration risk
if df["duration_sec"].mean() > 10:
    insights.append("⏳ Long fatigue event duration suggests slow response — improve alerting training.")

# Output insights
for i in insights:
    st.write("- " + i)


# ================= FOOTER ===========================
st.markdown("---")
st.caption("Powered by Streamlit — Mining Fatigue Intelligence System™")


