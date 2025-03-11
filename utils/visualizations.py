import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

def create_waste_distribution(current_data):
    """Create waste distribution pie chart with insights."""
    colors = {
        'Paper': 'rgb(139, 69, 19)',  # Brown
        'Plastic': 'rgb(30, 144, 255)',  # Blue
        'PET': 'rgb(34, 139, 34)',  # Green
        'Toxic': 'rgb(220, 20, 60)'   # Crimson
    }

    # Ensure current_data is in the correct format
    if isinstance(current_data, pd.DataFrame):
        current_data = current_data.set_index('waste_type')['amount']

    fig = go.Figure(data=[
        go.Pie(
            labels=list(current_data.index),
            values=list(current_data.values),
            marker_colors=[colors[waste] for waste in current_data.index],
            textinfo='percent+label+value',
            hovertemplate="%{label}: %{value:.1f}kg<extra></extra>",
            hole=0.4
        )
    ])

    fig.update_layout(
        title_text="Current Waste Distribution",
        showlegend=True,
        height=400,
        annotations=[{
            'text': f'Total: {current_data.sum():.1f}kg',
            'x': 0.5, 'y': 0.5,
            'font_size': 15,
            'showarrow': False
        }]
    )

    return fig

def create_time_analysis(historical_data, waste_types):
    """Create monthly and weekly analysis charts."""
    colors = {
        'Paper': 'rgb(139, 69, 19)',
        'Plastic': 'rgb(30, 144, 255)',
        'PET': 'rgb(34, 139, 34)',
        'Toxic': 'rgb(220, 20, 60)'
    }

    # Create subplots for monthly and weekly patterns
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Monthly Trends', 'Weekly Patterns'),
        row_heights=[0.6, 0.4],
        vertical_spacing=0.15
    )

    # Monthly trends
    monthly_data = historical_data.resample('M').mean()
    for waste_type in waste_types:
        fig.add_trace(
            go.Scatter(
                x=monthly_data.index,
                y=monthly_data[waste_type],
                name=waste_type,
                mode='lines+markers',
                line=dict(color=colors[waste_type], width=2),
                hovertemplate="%{y:.1f}kg<extra></extra>"
            ),
            row=1, col=1
        )

    # Weekly patterns
    weekly_avg = historical_data.groupby(historical_data.index.dayofweek).mean()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    for waste_type in waste_types:
        fig.add_trace(
            go.Bar(
                x=days,
                y=weekly_avg[waste_type],
                name=waste_type,
                marker_color=colors[waste_type],
                hovertemplate="%{y:.1f}kg<extra></extra>"
            ),
            row=2, col=1
        )

    fig.update_layout(
        height=800,
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Update axes labels
    fig.update_xaxes(title_text="Month", row=1, col=1)
    fig.update_xaxes(title_text="Day of Week", row=2, col=1)
    fig.update_yaxes(title_text="Average Amount (kg)", row=1, col=1)
    fig.update_yaxes(title_text="Average Amount (kg)", row=2, col=1)

    return fig

def get_waste_insights(historical_data):
    """Generate comprehensive insights about waste patterns."""
    insights = []

    # Calculate month-over-month growth
    monthly_totals = historical_data.resample('M').sum()
    if len(monthly_totals) >= 2:
        current_month = monthly_totals.iloc[-1].sum()
        prev_month = monthly_totals.iloc[-2].sum()
        mom_growth = ((current_month - prev_month) / prev_month) * 100
        insights.append({
            'title': 'Month-over-Month Growth',
            'value': f"{mom_growth:.1f}%",
            'description': "Change in total waste from previous month",
            'trend': '↑' if mom_growth > 0 else '↓',
            'color': 'green' if mom_growth > 0 else 'red'
        })

    # Calculate peak collection days
    daily_avg = historical_data.groupby(historical_data.index.dayofweek).mean()
    peak_day = daily_avg.sum(axis=1).idxmax()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    insights.append({
        'title': 'Peak Collection Day',
        'value': days[peak_day],
        'description': "Day with highest average collection",
        'trend': '📅',
        'color': 'blue'
    })

    # Calculate recycling efficiency
    total_waste = historical_data.sum().sum()
    recyclable = total_waste - historical_data['Toxic'].sum()
    recycling_rate = (recyclable / total_waste) * 100
    insights.append({
        'title': 'Recycling Efficiency',
        'value': f"{recycling_rate:.1f}%",
        'description': "Proportion of recyclable waste",
        'trend': '♻️',
        'color': 'green'
    })

    return insights

def create_prediction_chart(historical_data, predictions, waste_types):
    """Create an interactive chart showing historical data and predictions."""
    colors = {
        'Paper': 'rgb(139, 69, 19)',
        'Plastic': 'rgb(30, 144, 255)',
        'PET': 'rgb(34, 139, 34)',
        'Toxic': 'rgb(220, 20, 60)'
    }

    # Create subplots for trends and weekly patterns
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Waste Collection Trends and Predictions', 'Weekly Patterns'),
        row_heights=[0.7, 0.3]  
    )

    # Add historical data and predictions
    for waste_type in waste_types:
        # Historical trend
        fig.add_trace(
            go.Scatter(
                x=historical_data.index,
                y=historical_data[waste_type],
                name=f"{waste_type} (Historical)",
                mode='lines',
                line=dict(color=colors[waste_type], width=2)
            ),
            row=1, col=1
        )

        # Predictions with confidence band
        fig.add_trace(
            go.Scatter(
                x=predictions.index,
                y=predictions[waste_type],
                name=f"{waste_type} (Predicted)",
                mode='lines',
                line=dict(color=colors[waste_type], dash='dash'),
                opacity=0.7
            ),
            row=1, col=1
        )

        # Weekly patterns
        weekly_avg = historical_data[waste_type].groupby(historical_data.index.dayofweek).mean()
        fig.add_trace(
            go.Bar(
                x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                y=weekly_avg,
                name=waste_type,
                marker_color=colors[waste_type],
                showlegend=False
            ),
            row=2, col=1
        )

    fig.update_layout(
        height=800,
        hovermode='x unified',
        title_text="Waste Analysis Dashboard",
        xaxis2_title="Day of Week",
        yaxis_title="Amount (kg)",
        yaxis2_title="Average Amount (kg)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig

def create_summary_metrics(historical_data, predictions):
    """Create summary metrics with trend indicators."""
    latest_data = historical_data.iloc[-1]
    prev_data = historical_data.iloc[-2]
    future_data = predictions.iloc[0]

    metrics = []
    for waste_type in latest_data.index:
        current = latest_data[waste_type]
        previous = prev_data[waste_type]
        predicted = future_data[waste_type]

        trend = "↑" if predicted > current else "↓"
        change_percent = ((predicted - current) / current) * 100

        metrics.append({
            'waste_type': waste_type,
            'current': current,
            'trend': trend,
            'change': change_percent
        })

    return metrics
