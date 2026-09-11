from database import update_application_status, create_notification

def accept_application(app_id, reviewer_id, committee_name):
    """Accept an application"""
    update_application_status(app_id, 'Accepted', reviewer_id)
    return True

def reject_application(app_id, reviewer_id, reason=None, committee_name=None):
    """Reject an application"""
    update_application_status(app_id, 'Rejected', reviewer_id, reason)
    return True

def waitlist_application(app_id, reviewer_id):
    """Waitlist an application"""
    update_application_status(app_id, 'Waitlisted', reviewer_id)
    return True