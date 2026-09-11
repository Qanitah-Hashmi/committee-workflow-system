from database import create_notification

def notify_application_submitted(user_id, committee_name):
    create_notification(user_id, f"Your application to '{committee_name}' has been submitted.", 'success')

def notify_application_accepted(user_id, committee_name):
    create_notification(user_id, f"Your application to '{committee_name}' has been accepted!", 'success')

def notify_application_rejected(user_id, committee_name):
    create_notification(user_id, f"Your application to '{committee_name}' has been rejected.", 'error')

def notify_waitlisted(user_id, committee_name):
    create_notification(user_id, f"You have been waitlisted for '{committee_name}'. You will be notified if a slot becomes available.", 'info')

def notify_direct_assignment(user_id, committee_name, role):
    create_notification(user_id, f"You have been directly assigned to '{committee_name}' as {role}.", 'info')

def notify_removed_from_committee(user_id, committee_name, reason):
    create_notification(user_id, f"You have been removed from '{committee_name}'. Reason: {reason}", 'error')

def notify_committee_closed(user_id, committee_name):
    create_notification(user_id, f"The committee '{committee_name}' has been closed.", 'warning')

def notify_committee_cancelled(user_id, committee_name):
    create_notification(user_id, f"The committee '{committee_name}' has been cancelled.", 'error')

def notify_application_withdrawn(user_id, committee_name):
    create_notification(user_id, f"You have withdrawn your application from '{committee_name}'.", 'warning')

def notify_new_application_to_authority(authority_id, applicant_name, committee_name):
    create_notification(authority_id, f"New application received from {applicant_name} for '{committee_name}'.", 'info')

def notify_deadline_approaching(authority_id, committee_name, days_left):
    create_notification(authority_id, f"⏰ Deadline alert: '{committee_name}' closes in {days_left} day{'s' if days_left != 1 else ''}.", 'warning')

def notify_not_enough_applications(authority_id, committee_name, applications_count, total_seats):
    create_notification(authority_id, f"⚠️ '{committee_name}' has only {applications_count} applications for {total_seats} seats.", 'warning')

def notify_composition_not_met(authority_id, committee_name, missing_slots):
    create_notification(authority_id, f"⚠️ '{committee_name}' composition requirements not met. Missing: {missing_slots}.", 'warning')

def notify_seats_full(authority_id, committee_name):
    create_notification(authority_id, f"✅ All seats for '{committee_name}' have been filled.", 'success')

def notify_committee_published(user_id, committee_name):
    create_notification(user_id, f"📢 A new committee '{committee_name}' is now open for applications.", 'info')

def notify_approval_required(authority_id, committee_name, created_by_name):
    create_notification(authority_id, f"📋 Committee '{committee_name}' created by {created_by_name} requires your approval.", 'info')

def notify_committee_approved(user_id, committee_name):
    create_notification(user_id, f"✅ Your committee '{committee_name}' has been approved.", 'success')

def notify_committee_rejected(user_id, committee_name, reason):
    create_notification(user_id, f"❌ Your committee '{committee_name}' has been rejected. Reason: {reason}", 'error')