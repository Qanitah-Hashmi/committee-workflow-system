from database import get_audit_logs

def get_recent_actions(limit=50):
    """Get recent audit actions"""
    return get_audit_logs(limit)

def get_actions_by_user(user_id, limit=50):
    """Get audit actions by specific user"""
    logs = get_audit_logs(limit * 2)
    return [log for log in logs if log['user_id'] == user_id][:limit]

def get_actions_for_committee(committee_id, limit=50):
    """Get audit actions for specific committee"""
    logs = get_audit_logs(limit * 2)
    return [log for log in logs if log['target_type'] == 'committee' and log['target_id'] == committee_id][:limit]