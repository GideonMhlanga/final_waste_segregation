import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_historical_data(date_range):
    """Generate mock historical data for waste collection."""
    
    # Set date range
    end_date = datetime.now()
    if date_range == "Last Week":
        start_date = end_date - timedelta(days=7)
        freq = 'H'
    elif date_range == "Last Month":
        start_date = end_date - timedelta(days=30)
        freq = '6H'
    else:  # Last Year
        start_date = end_date - timedelta(days=365)
        freq = 'D'

    # Generate date range
    dates = pd.date_range(start=start_date, end=end_date, freq=freq)
    
    # Create base data with seasonal patterns
    data = {
        'Date': dates,
        'Paper': np.random.normal(loc=20, scale=5, size=len(dates)),
        'Plastic': np.random.normal(loc=15, scale=3, size=len(dates)),
        'PET': np.random.normal(loc=10, scale=2, size=len(dates)),
        'Toxic': np.random.normal(loc=5, scale=1, size=len(dates))
    }
    
    # Add weekly patterns
    for waste_type in ['Paper', 'Plastic', 'PET', 'Toxic']:
        data[waste_type] *= 1 + 0.3 * np.sin(2 * np.pi * dates.dayofweek / 7)
        # Ensure no negative values
        data[waste_type] = np.maximum(data[waste_type], 0)
    
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    
    return df
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_historical_data(time_range="Last Month"):
    """Generate sample historical data for waste types."""
    
    # Set date range based on selection
    end_date = datetime.now()
    if time_range == "Last Week":
        start_date = end_date - timedelta(days=7)
    elif time_range == "Last Month":
        start_date = end_date - timedelta(days=30)
    else:  # Last Year
        start_date = end_date - timedelta(days=365)
    
    # Generate date range
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Create waste patterns with some randomness
    data = {
        'Paper': np.random.normal(15, 3, len(date_range)),  # Mean 15kg, std 3kg
        'Plastic': np.random.normal(10, 2, len(date_range)),  # Mean 10kg, std 2kg
        'PET': np.random.normal(8, 1.5, len(date_range)),    # Mean 8kg, std 1.5kg
        'Toxic': np.random.normal(5, 1, len(date_range))     # Mean 5kg, std 1kg
    }
    
    # Add weekly patterns
    for i, date in enumerate(date_range):
        # Weekend drop in paper and increase in plastic
        if date.dayofweek in [5, 6]:  # Saturday and Sunday
            data['Paper'][i] *= 0.7
            data['Plastic'][i] *= 1.3
        
        # Ensure no negative values
        for waste_type in data:
            data[waste_type][i] = max(0.1, data[waste_type][i])
    
    # Create DataFrame
    df = pd.DataFrame(data, index=date_range)
    
    # Add seasonality for longer time periods
    if time_range == "Last Year":
        # Add seasonality - more waste in summer months
        for i, date in enumerate(date_range):
            seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * (date.dayofyear / 365))
            for waste_type in data:
                df.loc[date, waste_type] *= seasonal_factor
    
    return df
