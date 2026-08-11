from database import get_user_service_history

def calculate_current_workload(user_id):
    """Calculate current weekly workload for a user"""
    history = get_user_service_history(user_id)
    active = [h for h in history if h['status'] == 'Active']
    return sum(h['hours_per_week'] for h in active)

def get_workload_breakdown(user_id):
    """Get detailed workload breakdown"""
    history = get_user_service_history(user_id)
    active = [h for h in history if h['status'] == 'Active']
    
    return {
        'total_hours': sum(h['hours_per_week'] for h in active),
        'committees': len(active),
        'breakdown': [{'name': h['committee_name'], 'hours': h['hours_per_week']} for h in active]
    }