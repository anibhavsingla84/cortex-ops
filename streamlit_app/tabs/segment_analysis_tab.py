
import streamlit as st
import pandas as pd
from src.analytics import segment_analysis

def run_segment_analysis_tab(df):
    st.subheader("📊 Cohort & Segment Performance")

    st.markdown("Cohorts are grouped by origination vintage and FICO score buckets.")
    metrics = segment_analysis.segment_and_cohort_metrics(df)

    st.dataframe(metrics)
    st.download_button("Download Segment Report", metrics.to_csv(index=False), "segment_report.csv", "text/csv")
