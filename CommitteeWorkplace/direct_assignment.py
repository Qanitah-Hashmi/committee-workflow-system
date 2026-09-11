from database import direct_assign_member as db_direct_assign, create_notification, get_committee_by_id

def assign_member(committee_id, user_id, role, assigner_id, reason):
    """Directly assign a member to a committee"""
    success, message = db_direct_assign(committee_id, user_id, role, assigner_id, reason)
    if success:
        committee = get_committee_by_id(committee_id)
        committee_name = committee['name'] if committee else 'a committee'
        create_notification(user_id,
                           f"You have been directly assigned to '{committee_name}' as {role}.",
                           'success')
    return success, message