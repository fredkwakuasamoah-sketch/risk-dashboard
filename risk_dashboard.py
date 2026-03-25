import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import datetime

# ---------------- AUTO REFRESH ----------------
st_autorefresh(interval=60000, key="refresh")

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Risk Dashboard", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
body {background-color: #0E1117;}
.kpi-card {
    background: linear-gradient(135deg, #1f2c47, #2a3f5f);
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    color: white;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
}
.section {
    background-color: #111827;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown("<h1 style='text-align:center;color:#00C49F;'>📊 Risk Management Dashboard</h1>", unsafe_allow_html=True)

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.sidebar.file_uploader("📂 Upload Risk Log", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
else:
    df = pd.read_excel("RAID_log.xlsx")

df.columns = df.columns.str.strip()

# ---------------- FILTERS ----------------
st.sidebar.title("🔎 Filters")

status_filter = st.sidebar.multiselect(
    "Status",
    df["Status"].unique(),
    default=df["Status"].unique()
)

rating_filter = st.sidebar.multiselect(
    "Risk Rating",
    df["Risk Rating"].unique(),
    default=df["Risk Rating"].unique()
)

df = df[
    (df["Status"].isin(status_filter)) &
    (df["Risk Rating"].isin(rating_filter))
]

# ---------------- KPIs ----------------
total = len(df)
high = df[df["Risk Rating"] == "High"].shape[0]
open_risks = df[df["Status"] == "Open"].shape[0]
closed = df[df["Status"] == "Closed"].shape[0]

col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"<div class='kpi-card'><h3>📊 Total</h3><h1>{total}</h1></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='kpi-card'><h3>🔥 High</h3><h1>{high}</h1></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='kpi-card'><h3>⚠️ Open</h3><h1>{open_risks}</h1></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='kpi-card'><h3>✅ Resolved</h3><h1>{round((closed/total)*100,1) if total else 0}%</h1></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- INSIGHTS ----------------
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("🧠 Key Insights")

if total > 0:
    st.info(f"High risks represent {round((high/total)*100,1)}% of total risks.")

if not df.empty:
    top_issue = df["Risk Description"].value_counts().idxmax()
    st.write(f"Most frequent risk: **{top_issue[:80]}...**")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- ALERTS ----------------
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("🚨 Alerts")

if high > 10:
    st.error("🚨 CRITICAL: Too many high risks!")
elif high > 5:
    st.warning("⚠️ Moderate risk level")
else:
    st.success("✅ Risk level under control")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- TOP RISKS ----------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("🔝 Top 5 Risks")

    df["Short Risk"] = df["Risk Description"].astype(str).str[:50] + "..."
    top_risks = df["Short Risk"].value_counts().head(5)

    fig = px.bar(
        top_risks,
        orientation="h",
        color=top_risks.values,
        color_continuous_scale="Reds",
        template="plotly_dark"
    )

    fig.update_layout(yaxis=dict(automargin=True))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("🎯 Risk Rating")

    fig = px.pie(
        df,
        names="Risk Rating",
        hole=0.7,
        color_discrete_map={
            "High": "#FF4B4B",
            "Medium": "#FFA500",
            "Low": "#00C49F"
        }
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- TREND (FIXED) ----------------
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("📈 Risk Trend")

if "Date Raised" in df.columns:
    df["Date Raised"] = pd.to_datetime(df["Date Raised"], errors="coerce")

    # ✅ FIXED: no Period error
    df["Month"] = df["Date Raised"].dt.strftime("%Y-%m")

    trend = df.groupby("Month").size().reset_index(name="Count")

    fig = px.line(
        trend,
        x="Month",
        y="Count",
        title="Risks Over Time"
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- RESPONSE ----------------
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("📊 Response Breakdown")

response = df["Risk Response"].value_counts()

fig = px.pie(
    response,
    names=response.index,
    values=response.values,
    hole=0.5
)

st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------- DOWNLOAD ----------------
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("📥 Export")

csv = df.to_csv(index=False)

st.download_button(
    "Download Risk Report",
    csv,
    "risk_report.csv",
    "text/csv"
)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.caption(f"Last updated: {datetime.datetime.now()}")