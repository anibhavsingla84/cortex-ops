
import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.abspath("src"))
from waterfall_engine import waterfall_engine
from compliance_checks import checks
from compliance_checks import trigger_simulation
from reporting import lp_report
from llm_layer import llm_query
from llm_layer import agreement_parser
from forecast_engine import forecast
from audit import audit_logger
#from streamlit_app.tabs import segment_analysis_tab
from tabs import segment_analysis_tab

st.set_page_config(layout="wide")
st.title("CortexOps - Loan Ops Intelligence Prototype")

uploaded_file = st.file_uploader("Upload Loan Tape CSV", type="csv")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("Raw Loan Tape Preview")
    st.dataframe(df.head())
    audit_logger.log_event("Upload", f"Uploaded new loan tape with {len(df)} loans")

    st.subheader("Waterfall Output")
    output = waterfall_engine.apply_waterfall(df)
    st.dataframe(output.head())
    st.download_button("Download Waterfall Output", output.to_csv(index=False), "waterfall_output.csv", "text/csv")
    audit_logger.log_event("Waterfall Run", "Ran waterfall engine on uploaded loan tape")

    st.subheader("Concentration Limits Check (by state > 25%)")
    breaches = checks.check_concentration_limits(df)
    st.dataframe(breaches.reset_index().rename(columns={0: "Ratio"}))
    audit_logger.log_event("Compliance", "Checked concentration limits")

    st.subheader("LP Summary Report")
    report = lp_report.generate_lp_summary(df)
    st.table(report)
    audit_logger.log_event("Reporting", "Generated LP summary")

    st.subheader("Cash Flow Forecast (12 months)")
    if st.button("Run Forecast"):
        forecast_df, irr, nim = forecast.forecast_cashflows(df)
        st.dataframe(forecast_df.head(30))
        st.download_button("Download Forecast", forecast_df.to_csv(index=False), "loan_cashflow_forecast.csv", "text/csv")
        st.metric("Portfolio IRR", f"{irr:.2%}")
        st.metric("Net Interest Margin (NIM)", f"{nim:.2%}")
        audit_logger.log_event("Forecast", "Ran 12-month forecast")

        st.subheader("Trigger Breach Simulation")
        trigger_df = trigger_simulation.check_trigger_breaches(forecast_df)
        st.dataframe(trigger_df)
        st.download_button("Download Trigger Report", trigger_df.to_csv(index=False), "trigger_breach_report.csv", "text/csv")
        audit_logger.log_event("Trigger Check", "Simulated trigger breaches from forecast")

    st.subheader("📈 Future Originations")
    st.markdown("Enter expected new origination amounts for next 6 months (same structure as uploaded tape)")
    future_data = {}
    for i in range(1, 7):
        future_data[f"Month_{i}"] = st.number_input(f"Month {i} Origination Amount ($)", value=100000)

    if st.button("Simulate Future Originations"):
        sample_loan = df.iloc[0] if not df.empty else {}
        synthetic_loans = []
        for i, amount in enumerate(future_data.values()):
            num_loans = 10
            for j in range(num_loans):
                synthetic_loans.append({
                    "loan_id": f"new_{i+1}_{j+1}",
                    "current_principal_balance": amount / num_loans,
                    "interest_rate": sample_loan.get("interest_rate", 0.24),
                    "monthly_payment": sample_loan.get("monthly_payment", 200),
                    "loan_status": "current"
                })
        synthetic_df = pd.DataFrame(synthetic_loans)
        combined_df = pd.concat([df, synthetic_df], ignore_index=True)
        forecast_df, irr, nim = forecast.forecast_cashflows(combined_df)
        st.dataframe(forecast_df.head(30))
        st.metric("Combined IRR (with future origination)", f"{irr:.2%}")
        st.metric("Combined NIM", f"{nim:.2%}")
        trigger_df = trigger_simulation.check_trigger_breaches(forecast_df)
        st.subheader("Trigger Breach Simulation (with future origination)")
        st.dataframe(trigger_df)
        st.download_button("Download Combined Trigger Report", trigger_df.to_csv(index=False), "combined_trigger_report.csv", "text/csv")
        audit_logger.log_event("Simulation", "Simulated future originations and re-ran forecast and trigger checks")

    st.subheader("LLM-Powered Query")
    question = st.text_input("Ask a question about the loan tape")
    if question:
        try:
            response = llm_query.ask_llm_question(df, question)
            st.write(response)
            audit_logger.log_event("LLM Query", f"User question: {question}")
        except Exception as e:
            st.error(f"Error: {e}")

    st.subheader("📜 Legal Agreement Rule Extractor")
    legal_text = st.text_area("Paste a section from your warehouse or buyer agreement below:")
    if st.button("Extract Rules and Generate Code") and legal_text:
        with st.spinner("Extracting logic and generating Python..."):
            rule_struct = agreement_parser.extract_rules_from_text(legal_text)
            st.code(rule_struct, language="yaml")
            code_logic = agreement_parser.generate_code_from_rules(rule_struct)
            st.subheader("🔧 Generated Compliance Code")
            st.code(code_logic, language="python")
            audit_logger.log_event("Agreement Parsing", "Parsed warehouse/buyer agreement into code")

    
    st.subheader("📊 Segment Performance")
    segment_analysis_tab.run_segment_analysis_tab(df)


    st.subheader("🧾 Audit Trail")
    audit_log = audit_logger.read_audit_log()
    st.dataframe(audit_log)
    st.download_button("Download Audit Trail", audit_log.to_csv(index=False), "audit_log.csv", "text/csv")
