from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Proposal:
    def __init__(
        self,
        title: str,
        description: str,
        proposer_skills: List[str],
        required_skills: List[str],
        club_liquidity: float,
        project_budget: float,
        expected_timeline: int,  # in days
        market_demand_score: float,  # 0 to 1
        club_success_rate: float,  # 0 to 1
        risk_level: float,  # 0 to 1
        proposer_reputation_score: float  # 0 to 1
    ):
        self.title = title
        self.description = description
        self.proposer_skills = proposer_skills
        self.required_skills = required_skills
        self.club_liquidity = club_liquidity
        self.project_budget = project_budget
        self.expected_timeline = expected_timeline
        self.market_demand_score = market_demand_score
        self.club_success_rate = club_success_rate
        self.risk_level = risk_level
        self.proposer_reputation_score = proposer_reputation_score

existing_projects = [
    "AI-based financial risk assessment platform",
    "Blockchain-backed document verification",
    "Decentralized e-commerce payment gateway"
]

def get_innovation_score(proposal: Proposal) -> float:
    vectorizer = TfidfVectorizer()
    corpus = existing_projects + [proposal.description]
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    avg_similarity = similarity_scores.mean()
    
    # Higher similarity = Lower innovation score
    innovation_score = 1 - avg_similarity
    
    return innovation_score

def calculate_score(proposal: Proposal) -> float:
    # Skill Match
    skill_match = len(set(proposal.proposer_skills) & set(proposal.required_skills)) / len(proposal.required_skills) if proposal.required_skills else 0
    # Club Liquidity and Budget Ratio
    liquidity_score = min(1, proposal.club_liquidity / proposal.project_budget) if proposal.project_budget else 0
    # Timeline Feasibility (Assuming ideal timeline range is between 30–180 days)
    if proposal.expected_timeline < 30:
        timeline_score = 0.5  # Too short
    elif proposal.expected_timeline > 180:
        timeline_score = 0.5  # Too long
    else:
        timeline_score = 1  # Ideal range
    # Risk Adjustment (Higher risk = Lower score)
    risk_adjustment = 1 - proposal.risk_level
    # Compute Total Weighted Score
    total_score = (
        (skill_match * 0.20) +
        (liquidity_score * 0.15) +
        (timeline_score * 0.15) +
        (proposal.market_demand_score * 0.10) +
        (proposal.club_success_rate * 0.10) +
        (risk_adjustment * 0.05) +
        (proposal.proposer_reputation_score * 0.10) +
        (get_innovation_score(proposal) * 0.15)
    ) * 100
    return total_score


def evaluate_proposal(proposal: Proposal) -> str:
    score = calculate_score(proposal)
    
    if score >= 80:
        return f"✅ Approved! Score: {score:.2f} - Strong Proposal"
    elif score >= 50:
        return f"🔄 Needs Adjustment. Score: {score:.2f} - Consider improving weak points"
    else:
        return f"❌ Rejected. Score: {score:.2f} - Proposal needs significant improvement"


def generate_feedback_report(proposal: Proposal):
    score = calculate_score(proposal)
    return {
        "Proposal Title": proposal.title,
        "Total Score": f"{score:.2f}",
        "Recommendation": evaluate_proposal(proposal),
        "Weak Points": [
            "Skills gap" if len(set(proposal.proposer_skills) & set(proposal.required_skills)) < len(proposal.required_skills) else None,
            "Timeline too short" if proposal.expected_timeline < 30 else None,
            "High risk factor" if proposal.risk_level > 0.5 else None
        ]
    }

def calculate_backing_threshold(proposal: Proposal) -> float:
    '''
        AI will suggest a minimum backing threshold based on project scope and complexity.
        AI will analyze similar projects' success rates to adjust the threshold dynamically.
    '''
    base_threshold = proposal.project_budget * 0.1  # Minimum 10% of budget
    complexity_factor = (1 - proposal.risk_level) * 0.2  # Higher risk = Higher threshold
    
    return base_threshold + (base_threshold * complexity_factor)


proposal = Proposal(
    title="AI-Powered Investment Platform",
    description="An AI-based platform that automates investment decisions using Hedera's network.",
    proposer_skills=["Python", "AI", "Blockchain"],
    required_skills=["AI", "Hedera", "Finance"],
    club_liquidity=50000,
    project_budget=10000,
    expected_timeline=90,
    market_demand_score=0.8,
    club_success_rate=0.75,
    risk_level=0.2,
    proposer_reputation_score=0.9
)

result = evaluate_proposal(proposal)
print(result)


feedback = generate_feedback_report(proposal)
for key, value in feedback.items():
    print(f"{key}: {value}")


threshold = calculate_backing_threshold(proposal)
print(f"Suggested Backing Threshold: {threshold:.2f} QPT")