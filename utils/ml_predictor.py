import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import timedelta

def predict_waste(historical_data):
    """Generate waste predictions using simple linear regression."""
    
    predictions = pd.DataFrame()
    
    # Create future dates
    last_date = historical_data.index[-1]
    future_dates = pd.date_range(
        start=last_date + timedelta(days=1),
        periods=30,
        freq='D'
    )
    
    for waste_type in ['Paper', 'Plastic', 'PET', 'Toxic']:
        # Prepare features (days since start)
        X = np.array(range(len(historical_data))).reshape(-1, 1)
        y = historical_data[waste_type].values
        
        # Fit model
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict future values
        X_future = np.array(range(
            len(historical_data),
            len(historical_data) + len(future_dates)
        )).reshape(-1, 1)
        
        predictions[waste_type] = model.predict(X_future)
    
    predictions.index = future_dates
    return predictions