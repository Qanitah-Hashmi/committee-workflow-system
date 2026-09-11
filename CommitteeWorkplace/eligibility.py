from datetime import datetime
from database import get_connection, get_committee_composition, is_user_already_member, is_user_already_applied

def check_eligibility(user, committee):
    """Check if a user is eligible to apply to a committee"""
    
    # 1. Check status
    if committee['status'] not in ['Open', 'Under Review']:
        return False, "Committee is not open for applications."
    
    # 2. Check deadline - FIXED date comparison
    try:
        deadline_date = datetime.strptime(committee['deadline'], '%Y-%m-%d')
        if datetime.now() > deadline_date:
            return False, "Deadline has passed."
    except ValueError:
        return False, "Invalid deadline format."
    
    # 3. Check if already applied
    if is_user_already_applied(user['id'], committee['id']):
        return False, "You already have an active application."
    
    # 4. Check if already a member
    if is_user_already_member(user['id'], committee['id']):
        return False, "You are already a member of this committee."
    
    # 5. Check rank matches composition
    comp = get_committee_composition(committee['id'])
    eligible_slot = False
    
    for slot in comp:
        if slot['filled_slots'] < slot['total_slots']:
            if slot['rank_required'] == 'Any' or slot['rank_required'] == user.get('rank'):
                eligible_slot = True
                break
    
    if not eligible_slot:
        return False, "No eligible slots available for your rank."
    
    return True, "Eligible"