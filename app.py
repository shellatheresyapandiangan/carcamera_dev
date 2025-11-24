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

    col_operator = next((c for c in df.columns if "operator" in c or "driver" in c), None)
    col_shift = next((c for c in df.columns if "shift" in c), None)
    col_asset = next((c for c in df.columns if "asset" in c or "vehicle" in c or "fleet" in c), None)

    timestamp_cols = [c for c in df.columns if "gmt" in c or "time" in c or "date" in c]
    
    if len(timestamp_cols) >= 1:
        df["timestamp"] = pd.to_datetime(df[timestamp_cols[0]], errors="coerce")
        df["hour"] = df["timestamp"].dt.hour

    # Force Shift into only 1 and 2
    if col_shift:
        df[col_shift] = (
            df[col_shift]
            .astype(str)
            .str.extract(r"(\d+)")[0]
            .astype(float)
            .fillna(1)
            .astype(int)
            .clip(1, 2)
        )

    # Duration estimation
    if "hour" in df.columns:
        df["alert_weight"] = df["hour"].apply(lambda h: 3 if h in [1,2,3,4] else (2 if h in [0,5,6] else 1))

    return df, col_operator, col_shift, col_asset


df, col_operator, col_shift, col_asset = load_data()
st.success("📂 Data Loaded Successfully 🎉")

st.dataframe(df, use_container_width=True)


# ================= KEY SAFETY METRICS =================
st.subheader("📌 Key Safety Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Alerts", f"{len(df):,}")
col2.metric("Unique Operators", df[col_operator].nunique() if col_operator else "-")
col3.metric("Monitored Assets", df[col_asset].nunique() if col_asset else "-")
col4.metric("Highest Risk Hour", df["hour"].mode()[0] if "hour" in df else "-")


# ================= TREND ANALYTICS =====================
st.subheader("📈 Fatigue Trend Analysis")

fig_hour = px.line(
    df.groupby("hour").size().reset_index(name="alerts"),
    x="hour", y="alerts",
    markers=True,
    title="⏰ Fatigue Alerts by Hour"
)
st.plotly_chart(fig_hour, use_container_width=True)

# Shift
if col_shift:
    fig_shift = px.bar(
        df.groupby(col_shift).size().reset_index(name="alerts"),
        x=col_shift, y="alerts",
        title="👷 Fatigue Alerts by Shift"
    )
    st.plotly_chart(fig_shift, use_container_width=True)


# ================= SAFETY SCORING =====================
st.subheader("🏆 Operator Risk Index")

if col_operator:
    risk_df = df[col_operator].value_counts().reset_index(names=["operator", "alerts"])
    risk_df["safety_score"] = round((1 - (risk_df["alerts"] / risk_df["alerts"].max())) * 100)

    fig_risk = px.bar(
        risk_df.sort_values("safety_score"),
        x="safety_score", y="operator",
        orientation="h",
        title="🔍 Operator Risk Heatmap (Lower Score = High Risk)"
    )
    st.plotly_chart(fig_risk, use_container_width=True)

    st.write(risk_df)


# ================= AI INSIGHT ENGINE =====================
st.subheader("🧠 Automated Safety Insights")

insights = []

if "hour" in df:
    peak_hour = df["hour"].value_counts().idxmax()
    insights.append(f"⚠ Peak fatigue detected at **{peak_hour}:00** — consider microbreak scheduling.")

if col_shift:
    worst_shift = df[col_shift].value_counts().idxmax()
    insights.append(f"🔧 Shift **{worst_shift}** shows highest fatigue — review staffing & rest policy.")

if col_operator:
    worst_operator = df[col_operator].value_counts().idxmax()
    insights.append(f"🚨 Operator with highest alert: **{worst_operator}** — recommend coaching or rotation.")

for insight in insights:
    st.write("- " + insight)

st.markdown("---")
st.caption("© Fatigue Intelligence System — Safety & Predictive Monitoring Platform™")
