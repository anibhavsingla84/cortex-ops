
from datetime import datetime
import pandas as pd

#audit_log_path = "/mnt/data/CortexOps_Prototype/audit_trail.csv"
audit_log_path = "/mnt/data/audit_trail.csv"

def log_event(event_type, action, affected_loans="All", notes=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = pd.DataFrame([{
        "Timestamp": timestamp,
        "Event Type": event_type,
        "Action": action,
        "Affected Loans": affected_loans,
        "User Notes": notes
    }])
    try:
        existing = pd.read_csv(audit_log_path)
        updated = pd.concat([existing, log_entry], ignore_index=True)
    except FileNotFoundError:
        updated = log_entry
    updated.to_csv(audit_log_path, index=False)

def read_audit_log():
    try:
        return pd.read_csv(audit_log_path)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Timestamp", "Event Type", "Action", "Affected Loans", "User Notes"])
