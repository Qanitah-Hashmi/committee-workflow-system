from database import get_user_service_history

def get_service_summary(user_id):
    """Get service history summary for a user"""
    history = get_user_service_history(user_id)
    
    active = [h for h in history if h['status'] == 'Active']
    completed = [h for h in history if h['status'] == 'Completed']
    
    return {
        'total': len(history),
        'active': len(active),
        'completed': len(completed),
        'current_hours': sum(h['hours_per_week'] for h in active),
        'records': history
    }