import xgboost as xgb
import numpy as np
from sklearn.model_selection import train_test_split
from .models import Proposal, Performance

def get_training_data():
    proposals = Proposal.objects.select_related('performance').all()
    X = []
    y = []
    for proposal in proposals:
        X.append([
            proposal.budget,
            proposal.timeline,
            proposal.complexity,
            proposal.backing_qpt,
            proposal.peer_score,
            proposal.engagement_score,
            proposal.club.reputation_score
        ])
        y.append(proposal.performance.success_rate)

    return np.array(X), np.array(y)

def train_model():
    X, y = get_training_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100)
    model.fit(X_train, y_train)
    
    score = model.score(X_test, y_test)
    print(f"Model Score: {score:.2f}")

train_model()
