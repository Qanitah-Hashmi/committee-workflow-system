from database import update_committee_status, log_audit, create_notification

def submit_for_approval(committee_id, user_id):
    """Submit committee for approval"""
    update_committee_status(committee_id, 'Pending Approval', user_id)
    return True

def approve_committee(committee_id, user_id):
    """Approve committee"""
    update_committee_status(committee_id, 'Approved', user_id)
    return True

def publish_committee(committee_id, user_id):
    """Publish committee (make open for applications)"""
    update_committee_status(committee_id, 'Open', user_id)
    return True

def close_committee(committee_id, user_id):
    """Close committee"""
    update_committee_status(committee_id, 'Closed', user_id)
    return True

def archive_committee(committee_id, user_id):
    """Archive committee"""
    update_committee_status(committee_id, 'Archived', user_id)
    return True

def cancel_committee(committee_id, user_id):
    """Cancel committee"""
    update_committee_status(committee_id, 'Cancelled', user_id)
    return True