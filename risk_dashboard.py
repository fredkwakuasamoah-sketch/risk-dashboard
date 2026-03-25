import streamlit as st
import pandas as pd
import plotly.express as px

# AI imports
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Risk Dashboard", layout="wide")

st.markdown("<h1 style='text-align:center;color:#00C49F;'>📊 Risk Log Dashboard</h1>", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
df = pd.read_excel("RAID_log.xlsx")

# 🔥 CLEAN COLUMN NAMES
df.columns = df.columns.str.strip()

# 🔍 OPTIONAL: SEE COLUMNS
# st.write(df.columns)

# ---------------- SELECT ONLY NEEDED COLUMNS ----------------
columns_needed = ["Risk Response", "Risk Description", "Risk Rating", "Status"]

df = df[columns_needed]

# ---------------- FILTERS ----------------
st.sidebar.title("🔎 Filters")

status_filter = st.sidebar.multiselect(
    "Select Status",
    df["Status"].unique(),
    default=df["Status"].unique()
)

rating_filter = st.sidebar.multiselect(
    "Select Risk Rating",
    df["Risk Rating"].unique(),
    default=df["Risk Rating"].unique()
)

df = df[
    (df["Status"].isin(status_filter)) &
    (df["Risk Rating"].isin(rating_filter))
]

# ---------------- KPIs ----------------
st.subheader("📊 Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Risks", len(df))
col2.metric("Open Risks", df[df["Status"] == "Open"].shape[0])
col3.metric("High Risks", df[df["Risk Rating"] == "High"].shape[0])

st.markdown("---")

# ---------------- RISK RATING CHART ----------------
st.subheader("📊 Risk Rating Distribution")

fig_rating = px.bar(
    df["Risk Rating"].value_counts(),
    title="Risk Rating Count",
    labels={"value": "Count", "index": "Risk Rating"}
)

st.plotly_chart(fig_rating, use_container_width=True)

# ---------------- STATUS PIE CHART ----------------
st.subheader("📌 Risk Status Breakdown")

fig_status = px.pie(
    df,
    names="Status",
    title="Risk Status"
)

st.plotly_chart(fig_status, use_container_width=True)

st.markdown("---")

# ---------------- TOP RISKS TABLE ----------------
st.subheader("⚠️ Risk Log Table")

st.dataframe(df)

st.markdown("---")

# ---------------- AI SECTION ----------------
st.subheader("🤖 AI Prediction (Based on Rating)")

ml_df = df.dropna()

if not ml_df.empty:

    encoder = LabelEncoder()
    ml_df["Rating_encoded"] = encoder.fit_transform(ml_df["Risk Rating"])

    X = ml_df[["Rating_encoded"]]
    y = ml_df["Status"]

    model = RandomForestClassifier()
    model.fit(X, y)

    ml_df["Predicted Status"] = model.predict(X)

    st.dataframe(
        ml_df[
            [
                "Risk Description",
                "Risk Rating",
                "Status",
                "Predicted Status"
            ]
        ]
    )
else:
    st.warning("Not enough data for AI")