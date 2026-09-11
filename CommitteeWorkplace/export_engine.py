import pandas as pd
from datetime import datetime
from database import get_all_committees, get_all_users, get_audit_logs

def export_committees():
    """Export committees to DataFrame"""
    committees = get_all_committees()
    return pd.DataFrame(committees)

def export_users():
    """Export users to DataFrame (without sensitive data)"""
    users = get_all_users()
    df = pd.DataFrame(users)
    return df[['id', 'email', 'name', 'role', 'department', 'school', 'rank', 'created_at']]

def export_audit_logs(limit=1000):
    """Export audit logs to DataFrame"""
    logs = get_audit_logs(limit)
    return pd.DataFrame(logs)

def generate_filename(prefix):
    """Generate filename with timestamp"""
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"