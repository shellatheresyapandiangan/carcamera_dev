# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# --------------------------
# Config
# --------------------------
st.set_page_config(
    page_title="Fatigue Detection & Safety Dashboard",
    layout="wide",
    page_icon="😴",
)

# Styling (simple)
st.markdown("""
    <style>
    .big-font { font-size:20px !important; }
    .kpi {background:#fff; padding:12px; border-radius:8px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);}
    </style>
""", unsafe_allow_html=True)

# --------------------------
# Data load (default: local path)
# --------------------------
df = "manual fatique.xlsx"

# --------------------------
# Basic cleaning & normalize columns
# --------------------------
df.columns = df.columns.str.strip()
# lower & replace spaces with underscores for programmatic use
df.columns = [c.lower().replace(" ", "_") for c in df.columns]

# detect time columns (common in your file)
time_candidates = [c for c in df.columns if "gmt" in c or "time" in c or "date" in c or "timestamp" in c]
start_col = time_candidates[0] if len(time_candidates) > 0 else None
end_col = time_candidates[1] if len(time_candidates) > 1 else None

# attempt parse
if start_col:
    df["start"] = pd.to_datetime(df[start_col], errors="coerce")
else:
    df["start"] = pd.NaT

if end_col:
    df["end"] = pd.to_datetime(df[end_col], errors="coerce")
else:
    df["end"] = pd.NaT

df["duration_sec"] = (df["end"] - df["start"]).dt.total_seconds()

# Detect key columns
col_operator = next((c for c in df.columns if "operator" in c or "nik" in c), None)
col_fleet = next((c for c in df.columns if "fleet" in c or "asset" in c or "fleet_number" in c), None)
col_alarm = next((c for c in df.columns if "alarm" in c or "fatigue" in c or "alarm_type" in c), None)
col_shift = next((c for c in df.columns if "shift" in c), None)
col_speed = next((c for c in df.columns if "km" in c or "speed" in c or "in_km" in c), None)
col_qc = next((c for c in df.columns if "qc" in c or "validation" in c), None)

# Make friendly names for display
display_cols = {
    "Operator": col_operator,
    "Fleet/Asset": col_fleet,
    "Alarm Type": col_alarm,
    "Shift": col_shift,
    "Start Time": "start",
    "End Time": "end",
    "Duration (s)": "duration_sec",
    "Speed": col_speed,
    "QC": col_qc
}

# --------------------------
# Sidebar filters
# --------------------------
st.sidebar.header("Filters")
date_min = df["start"].min() if df["start"].notnull().any() else None
date_max = df["start"].max() if df["start"].notnull().any() else None

if date_min is not None:
    date_range = st.sidebar.date_input("Date range", value=(date_min.date(), date_max.date() if date_max is not None else date_min.date()))
else:
    date_range = None

operator_options = list(df[col_operator].dropna().unique()) if col_operator else []
sel_operator = st.sidebar.multiselect("Operators", options=operator_options, default=[])

fleet_options = list(df[col_fleet].dropna().unique()) if col_fleet else []
sel_fleet = st.sidebar.multiselect("Fleets / Assets", options=fleet_options, default=[])

sel_shift = st.sidebar.multiselect("Shift", options=sorted(df[col_shift].dropna().unique().tolist()) if col_shift else [], default=[])

# Apply filters
df_filtered = df.copy()
if date_range and date_min is not None:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    df_filtered = df_filtered[(df_filtered["start"] >= start_date) & (df_filtered["start"] <= end_date)]

if sel_operator:
    df_filtered = df_filtered[df_filtered[col_operator].isin(sel_operator)]

if sel_fleet:
    df_filtered = df_filtered[df_filtered[col_fleet].isin(sel_fleet)]

if sel_shift:
    df_filtered = df_filtered[df_filtered[col_shift].isin(sel_shift)]

# --------------------------
# Header / KPIs
# --------------------------
col1, col2, col3, col4 = st.columns([2,2,2,2])
col1.markdown("### ✅ Total Alerts")
col1.markdown(f"#### {len(df_filtered):,}")

col2.markdown("### 👷 Unique Operators")
col2.markdown(f"#### {df_filtered[col_operator].nunique() if col_operator else 0}")

col3.markdown("### 🚛 Unique Assets / Fleets")
col3.markdown(f"#### {df_filtered[col_fleet].nunique() if col_fleet else 0}")

col4.markdown("### ⏱ Avg Duration (s)")
avg_dur = df_filtered["duration_sec"].dropna().mean()
col4.markdown(f"#### {avg_dur:.1f}" if not np.isnan(avg_dur) else "#### -")

st.markdown("---")

# --------------------------
# Time series: Alerts over time
# --------------------------
st.subheader("📈 Fatigue Alerts Over Time")
if df_filtered["start"].notnull().any():
    ts = df_filtered.set_index("start").resample("D").size().reset_index(name="alerts")
    fig_ts = px.line(ts, x="start", y="alerts", markers=True, title="Daily Alerts")
    st.plotly_chart(fig_ts, use_container_width=True)
else:
    st.info("Timestamp tidak tersedia untuk grafik time-series.")

# --------------------------
# Hourly pattern & shift heatmap
# --------------------------
st.subheader("🕒 Hourly Pattern & Shift Distribution")
if df_filtered["start"].notnull().any():
    df_filtered["hour"] = df_filtered["start"].dt.hour
    hourly = df_filtered.groupby("hour").size().reindex(range(0,24), fill_value=0)
    fig_hour = go.Figure()
    fig_hour.add_trace(go.Bar(x=hourly.index, y=hourly.values))
    fig_hour.update_layout(title="Alerts by Hour", xaxis_title="Hour of day", yaxis_title="Count")
    st.plotly_chart(fig_hour, use_container_width=True)

    if col_shift:
        shift_counts = df_filtered.groupby(col_shift).size().reset_index(name="count")
        fig_shift = px.pie(shift_counts, names=col_shift, values="count", title="Distribution by Shift")
        st.plotly_chart(fig_shift, use_container_width=True)
else:
    st.info("Timestamp tidak tersedia untuk hourly/shift analysis.")

# --------------------------
# Top Operators & Fleets
# --------------------------
st.subheader("🏅 Top Operators & Assets")
left, right = st.columns(2)

with left:
    if col_operator:
        top_ops = df_filtered[col_operator].value_counts().head(10).reset_index()
        top_ops.columns = [col_operator, "count"]
        fig_ops = px.bar(top_ops, x=col_operator, y="count", title="Top Operators by Alerts")
        st.plotly_chart(fig_ops, use_container_width=True)
        st.table(top_ops)

with right:
    if col_fleet:
        top_fleet_df = df_filtered[col_fleet].value_counts().head(10).reset_index()
        top_fleet_df.columns = [col_fleet, "count"]
        fig_fleet = px.bar(top_fleet_df, x=col_fleet, y="count", title="Top Fleets / Assets by Alerts")
        st.plotly_chart(fig_fleet, use_container_width=True)
        st.table(top_fleet_df)

# --------------------------
# QC / Validation status
# --------------------------
if col_qc:
    st.subheader("🔎 QC / Validation Status")
    qc_counts = df_filtered[col_qc].value_counts().reset_index()
    qc_counts.columns = [col_qc, "count"]
    st.table(qc_counts)
    fig_qc = px.bar(qc_counts, x=col_qc, y="count", title="QC Status")
    st.plotly_chart(fig_qc, use_container_width=True)

# --------------------------
# Data table & export
# --------------------------
st.subheader("📄 Sample Data & Export")
st.dataframe(df_filtered[ list(display_cols.values()) ].rename(columns={v:k for k,v in display_cols.items() if v in df_filtered.columns}).head(200), use_container_width=True)

# Export CSV
@st.cache_data
def to_csv_bytes(df_in):
    return df_in.to_csv(index=False).encode('utf-8')

csv_bytes = to_csv_bytes(df_filtered)
st.download_button("⬇️ Download filtered CSV", data=csv_bytes, file_name="fatigue_filtered.csv", mime="text/csv")

# --------------------------
# Automated Insights / Text summary
# --------------------------
st.subheader("🧠 Auto Insights")
insights = []
# Highest alert hour
if "hour" in df_filtered.columns and df_filtered["hour"].notnull().any():
    peak_hour = int(df_filtered.groupby("hour").size().idxmax())
    insights.append(f"⏰ Jam paling rawan: {peak_hour}:00 — pertimbangkan break policy di jam ini.")
# Worst operator
if col_operator:
    worst_op = df_filtered[col_operator].value_counts().idxmax()
    insights.append(f"⚠️ Operator dengan alert terbanyak: {worst_op} — pertimbangkan coaching & review assignment.")
# Fleet
if col_fleet:
    worst_fleet = df_filtered[col_fleet].value_counts().idxmax()
    insights.append(f"🚛 Asset dengan alert terbanyak: {worst_fleet} — cek kondisi kendaraan & rute.")
# QC ratio
if col_qc:
    valid = df_filtered[df_filtered[col_qc].str.contains("yes|validated|valid", case=False, na=False)].shape[0]
    total = df_filtered.shape[0]
    ratio = valid / total * 100 if total>0 else 0
    insights.append(f"✅ Rasio QC valid: {ratio:.1f}% — kualitas validasi data penting untuk kepercayaan analisa.")

for s in insights:
    st.info(s)

# --------------------------
# Feature ideas / CTA for sales
# --------------------------
st.markdown("---")
st.markdown("## 🚀 Next & Add-on Features (siap dijual ke enterprise)")
st.markdown("""
- Real-time streaming ingestion (Kafka / MQTT) untuk monitoring live.
- Alerts & notification engine (Slack / SMS / Email) + escalation workflow.
- Integration with telematics (GPS) untuk heatmaps rute & hotspot analysis.
- Predictive fatigue model (per-operator risk score) dengan ML.
- Role-based access & audit trail (enterprise-ready).
""")

st.caption("Data source: default path `/mnt/data/manual fatique.xlsx` (ubah di app.py sesuai kebutuhan).")
