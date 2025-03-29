from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib, random
from typing import List

class AIProposal:
    def __init__(
        self,
        title: str,
        description: str,
        #proposer_skills: List[str],
        #required_skills: List[str],
        club_liquidity: float,
        project_budget: float,
        expected_timeline: int,  # in days
        market_demand_score: float,  # 0 to 1
        club_success_rate: float,  # 0 to 1
        risk_level: float,  # 0 to 1
        proposer_reputation_score: float,  # 0 to 1
        complexity: float
    ):
        self.title = title
        self.description = description
        #self.proposer_skills = proposer_skills
        #self.required_skills = required_skills
        self.club_liquidity = club_liquidity
        self.project_budget = project_budget
        self.expected_timeline = expected_timeline
        self.market_demand_score = market_demand_score
        self.club_success_rate = club_success_rate
        self.risk_level = risk_level
        self.proposer_reputation_score = proposer_reputation_score
        self.complexity = complexity

existing_projects = [
    "AI-based financial risk assessment platform",
    "Blockchain-backed document verification",
    "Decentralized e-commerce payment gateway"
]

# === Generate Synthetic Training Data ===
def generate_training_data(num_samples: int = 500) -> pd.DataFrame:
    data = []
    
    for _ in range(num_samples):
        budget = random.randint(1, 500000)
        timeline = random.randint(1, 365)
        complexity = random.uniform(0.1, 1.0)
        peer_score = random.uniform(0.0, 1.0)
        engagement_score = peer_score * 100
        club_success_rate = random.uniform(0.0, 1.0)
        risk_level = random.uniform(0.0, 1.0)
        proposer_reputation_score = random.uniform(0.0, 1.0)
        
        if (
            club_success_rate > 0.6 and
            risk_level < 0.5 and
            proposer_reputation_score > 0.7 and
            peer_score > 0.5
        ):
            outcome = 1
        else:
            outcome = 0

        proposal = {
            'budget': budget,
            'timeline': timeline,
            'complexity': complexity,
            'peer_score': peer_score,
            'engagement_score': engagement_score,
            'club_success_rate': club_success_rate,
            'risk_level': risk_level,
            'proposer_reputation_score': proposer_reputation_score,
            'outcome': outcome
        }
        data.append(proposal)

    df = pd.DataFrame(data)
    return df

# === Train AI Model ===
def train_model():
    df = generate_training_data(1000)

    X = df.drop('outcome', axis=1)
    y = df['outcome']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"✅ Model trained with accuracy: {accuracy:.2f}")

    joblib.dump(model, 'proposal_prediction_model.pkl')
    print("✅ Model saved to 'proposal_prediction_model.pkl'")

    return model

def get_innovation_score(proposal: AIProposal) -> float:
    vectorizer = TfidfVectorizer()
    corpus = existing_projects + [proposal.description]
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    avg_similarity = similarity_scores.mean()
    
    # Higher similarity = Lower innovation score
    innovation_score = 1 - avg_similarity
    
    return innovation_score

def calculate_score(proposal: AIProposal) -> float:
    # Skill Match
    skill_match = 1#len(set(proposal.proposer_skills) & set(proposal.required_skills)) / len(proposal.required_skills) if proposal.required_skills else 0

    # Club Liquidity and Budget Ratio
    liquidity_score = min(1, proposal.club_liquidity / proposal.project_budget) if proposal.project_budget else 0

    # Timeline Feasibility (Assuming ideal timeline range is between 30–180 days)
    if proposal.expected_timeline < 30:
        timeline_score = 0.2
    elif proposal.expected_timeline > 180:
        timeline_score = 0.4
    else:
        timeline_score = 1.0

    # Market Demand
    market_demand_score = proposal.market_demand_score

    # Innovation Score
    innovation_score = get_innovation_score(proposal)

    # Club Success Rate
    club_success_score = proposal.club_success_rate

    # Risk Level (Lower is better)
    risk_score = 1 - proposal.risk_level

    # Proposer Reputation
    reputation_score = proposal.proposer_reputation_score

    # Weighted sum of all factors
    score = (
        (skill_match * 0.15) +
        (liquidity_score * 0.10) +
        (timeline_score * 0.10) +
        (market_demand_score * 0.10) +
        (innovation_score * 0.10) +
        (club_success_score * 0.10) +
        (risk_score * 0.15) +
        (reputation_score * 0.20)
    )
    prob = score * 100
    if score >= 0.7:
        return f"✅ Approved! Score: {prob}% - Strong Proposal"
    elif score >= 0.5:
        return f"🔄 Needs Adjustment. Score: {prob}% - Consider improving weak points"
    else:
        return f"❌ Rejected. Score: {prob}% - Proposal needs significant improvement"
    #return score

model = train_model()

def evaluate_proposal(proposal: AIProposal) -> str:
    if not model:
        return "Model not trained yet."

    data = {
        'budget': proposal.project_budget,
        'timeline': proposal.expected_timeline,
        'complexity': proposal.complexity,
        'peer_score': 1,
        'engagement_score': 100,
        'club_success_rate': proposal.club_success_rate,
        'risk_level': proposal.risk_level,
        'proposer_reputation_score': proposal.proposer_reputation_score
    }

    prediction = model.predict([list(data.values())])[0]
    probability = model.predict_proba([list(data.values())])[0][1] * 100
    print(prediction)
    if probability >= 75:
        return f"✅ Approved! Score: {probability:.2f}% - Strong Proposal"
    elif probability >= 50:
        return f"🔄 Needs Adjustment. Score: {probability:.2f}% - Consider improving weak points"
    else:
        return f"❌ Rejected. Score: {probability:.2f}% - Proposal needs significant improvement"


def generate_feedback_report(proposal: AIProposal):
    score = calculate_score(proposal)
    return {
        "Proposal Title": proposal.title,
        "Total Score": f"{score}",
        #"Recommendation": evaluate_proposal(proposal),
        "Weak Points": [
            #"Skills gap" if len(set(proposal.proposer_skills) & set(proposal.required_skills)) < len(proposal.required_skills) else None,
            "Timeline too short" if proposal.expected_timeline < 30 else None,
            "High risk factor" if proposal.risk_level > 0.5 else None
        ]
    }

def calculate_backing_threshold(proposal: AIProposal) -> float:
    '''
        AI will suggest a minimum backing threshold based on project scope and complexity.
        AI will analyze similar projects' success rates to adjust the threshold dynamically.
    '''
    base_threshold = proposal.project_budget * 0.1  # Minimum 10% of budget
    complexity_factor = (1 - proposal.risk_level) * 0.2  # Higher risk = Higher threshold
    
    return base_threshold + (base_threshold * complexity_factor)



'''
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
print(f"Suggested Backing Threshold: {threshold:.2f} QPT")'
'''