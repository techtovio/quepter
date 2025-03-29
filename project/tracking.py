from .models import Proposal
from django.core.mail import send_mail

def get_project_status(proposal_id: str):
    proposal = Proposal.objects.get(id=proposal_id)
    return {
        "title": proposal.title,
        "milestones_completed": proposal.milestones_completed,
        "total_milestones": proposal.total_milestones,
        "budget_used": proposal.budget_used,
        "total_budget": proposal.total_budget
    }

def notify_project_owner(proposal_id: str, completion_rate: float, budget_ratio: float):
    proposal = Proposal.objects.get(id=proposal_id)
    user = proposal.created_by

    message = f"""
    🚨 Project Alert!
    Your project '{proposal.title}' is experiencing issues:
    - Completion Rate: {completion_rate * 100:.2f}%
    - Budget Used: {budget_ratio * 100:.2f}%
    Please take action to avoid further delays.
    """

    send_mail(
        subject="🚨 Project Issue Detected",
        message=message,
        from_email="noreply@quepter.com",
        recipient_list=[user.email],
        fail_silently=False
    )


def track_project_progress(proposal_id: str):
    status = get_project_status(proposal_id)
    
    completion_rate = status['milestones_completed'] / status['total_milestones']
    budget_ratio = status['budget_used'] / status['total_budget']
    
    # Adjust AI model based on real-time data
    risk_adjustment = (1 - completion_rate) * 20
    feasibility_adjustment = min((status['total_budget'] / status['milestones_completed']) * 10, 40)
    
    score = feasibility_adjustment + (completion_rate * 30) - (risk_adjustment)
    
    # Send Notifications if delays or budget issues
    if completion_rate < 0.5 or budget_ratio > 0.8:
        notify_project_owner(proposal_id, completion_rate, budget_ratio)
    
    return round(score, 2)
