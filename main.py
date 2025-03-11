import streamlit as st
import sys
import os
from sqlalchemy import func, cast, Numeric


# Add the current directory to the path so Python can find the modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Waste Segregation Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
from datetime import datetime, timedelta
from utils.data_generator import generate_historical_data
from utils.ml_predictor import predict_waste
from utils.visualizations import (
    create_waste_distribution,
    create_time_analysis,
    get_waste_insights,
    create_prediction_chart,
    create_summary_metrics
)
from pages.auth import show_auth_page
from pages.profile import show_profile_page
from pages.admin import show_admin_panel
from models.database import get_session, WasteEntry
from sqlalchemy import func

# Load custom CSS
with open('assets/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if 'user' not in st.session_state:
    st.session_state['user'] = None

# Authentication check
if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
    show_auth_page()
else:
    user = st.session_state['user']

    # Title and description
    st.title("🗑️ Waste Segregation Analytics Dashboard")
    st.markdown(f"""
    Welcome, **{user.username}** from **{user.department}** department!
    This interactive dashboard provides comprehensive insights into waste segregation patterns.
    """)

    # Sidebar filters
    st.sidebar.header("📊 Analysis Controls")

    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")

        if st.session_state['authenticated']:
            st.write(f"Welcome, {st.session_state['user'].username}!")

            if 'current_page' not in st.session_state:
                st.session_state['current_page'] = 'dashboard'

            # Dashboard button
            if st.button("Dashboard", use_container_width=True):
                st.session_state['current_page'] = 'dashboard'
                st.rerun()

            # Analysis button
            if st.button("Analysis", use_container_width=True):
                st.session_state['current_page'] = 'analysis'
                st.rerun()

            # Data Entry button
            if st.button("Data Entry", use_container_width=True):
                st.session_state['current_page'] = 'data_entry'
                st.rerun()

            # Profile button
            if st.button("My Profile", use_container_width=True):
                st.session_state['current_page'] = 'profile'
                st.rerun()

            # Admin panel for admin users
            if st.session_state['user'].job_title.lower() in ['admin', 'administrator', 'manager']:
                if st.button("Admin Panel", use_container_width=True):
                    st.session_state['current_page'] = 'admin'
                    st.rerun()

            # Settings button
            if st.button("Settings", use_container_width=True):
                st.session_state['current_page'] = 'settings'
                st.rerun()

            # Logout button
            if st.button("Logout", use_container_width=True):
                st.session_state['authenticated'] = False
                st.session_state['user'] = None
                st.session_state['current_page'] = 'auth'
                st.rerun()
        else:
            st.info("Please log in to access the dashboard.")

    date_range = st.sidebar.selectbox(
        "Time Range",
        ["Last Week", "Last Month", "Last Year"],
        help="Select the time period for analysis"
    )

    waste_type = st.sidebar.multiselect(
        "Waste Types",
        ["Paper", "Plastic", "PET", "Toxic"],
        default=["Paper", "Plastic", "PET", "Toxic"],
        help="Choose which types of waste to display"
    )

    department_filter = st.sidebar.selectbox(
        "Department Filter",
        ["All Departments", user.department],
        help="Filter data by department"
    )

    # Get data from database
    session = get_session()
    query = session.query(
        WasteEntry.waste_type,
        func.round(cast(func.sum(WasteEntry.amount), Numeric(10, 2)), 2).label('total_amount'),
        func.to_char(WasteEntry.timestamp, 'YYYY-MM-DD').label('date'),  # Extract date
        func.to_char(WasteEntry.timestamp, 'HH24:MI:SS').label('time')  # Extract time
    )

    if department_filter != "All Departments":
        query = query.filter(WasteEntry.department == department_filter)

    query = query.group_by(
        WasteEntry.waste_type,
        func.to_char(WasteEntry.timestamp, 'YYYY-MM-DD').label('date'),  # Extract date
        func.to_char(WasteEntry.timestamp, 'HH24:MI:SS').label('time')  # Extract time
    )

    results = query.all()

    # Convert to DataFrame
    if results:
        historical_data = pd.DataFrame(results)
        historical_data.set_index('date', inplace=True)
    else:
        historical_data = generate_historical_data(date_range)  # Use mock data if no real data

    # Layout
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📊 Current Distribution")
        dist_fig = create_waste_distribution(historical_data.iloc[-1])
        st.plotly_chart(dist_fig, use_container_width=True)

        # Add waste entry form
        st.subheader("➕ Add Waste Entry")
        with st.form("waste_entry"):
            new_waste_type = st.selectbox("Waste Type", ["Paper", "Plastic", "PET", "Toxic"])
            amount = st.number_input("Amount (kg)", min_value=0.1, step=0.1)

            if st.form_submit_button("Add Entry"):
                new_entry = WasteEntry(
                    user_id=user.id,
                    department=user.department,
                    waste_type=new_waste_type,
                    amount=amount
                )
                session.add(new_entry)
                session.commit()
                st.success("Entry added successfully!")
                st.rerun()

        # Key Insights
        st.subheader("💡 Key Insights")
        insights = get_waste_insights(historical_data)

        for insight in insights:
            st.info(
                f"""
                **{insight['title']}**

                {insight['trend']} {insight['value']}

                _{insight['description']}_
                """
            )

    with col2:
        st.subheader("📈 Time Analysis")
        time_fig = create_time_analysis(historical_data[waste_type], waste_type)
        st.plotly_chart(time_fig, use_container_width=True)

        # Add ML predictions
        st.subheader("🔮 Waste Forecasting")

        # Generate predictions using our ML model
        predictions = predict_waste(historical_data)

        # Create prediction visualization
        pred_fig = create_prediction_chart(historical_data, predictions, waste_type)
        st.plotly_chart(pred_fig, use_container_width=True)

        # Display summary metrics with trend indicators
        st.subheader("📊 Forecast Metrics")
        metrics = create_summary_metrics(historical_data, predictions)

        # Display metrics in columns
        metric_cols = st.columns(len(metrics))
        for i, metric in enumerate(metrics):
            with metric_cols[i]:
                st.metric(
                    label=metric['waste_type'],
                    value=f"{metric['current']:.1f} kg",
                    delta=f"{metric['change']:.1f}%",
                    delta_color="normal"
                )

    # Department Statistics
    st.subheader("📋 Department Statistics")

    # Get department statistics
    dept_stats = session.query(
        WasteEntry.department,
        func.sum(WasteEntry.amount).label('total_amount'),
        func.count(WasteEntry.id).label('entry_count')
    ).group_by(WasteEntry.department).all()

    if dept_stats:
        # Create tabs for different department views
        dept_tab1, dept_tab2 = st.tabs(["Department Metrics", "Department Comparison"])

        with dept_tab1:
            # Display department metrics in cards
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            dept_cols = st.columns(len(dept_stats))

            for i, (dept, total, count) in enumerate(dept_stats):
                with dept_cols[i]:
                    st.markdown(f"""
                    <div class="department-card">
                        <h3>{dept}</h3>
                        <p class="metric-value">{total:.1f} kg</p>
                        <p class="metric-title">Total Waste ({count} entries)</p>
                    </div>
                    """, unsafe_allow_html=True)

        with dept_tab2:
            # Create department comparison chart
            import plotly.express as px

            dept_df = pd.DataFrame([
                {"Department": dept, "Total Waste (kg)": total, "Entry Count": count}
                for dept, total, count in dept_stats
            ])

            fig = px.bar(
                dept_df, 
                x="Department", 
                y="Total Waste (kg)",
                color="Department",
                text="Total Waste (kg)",
                title="Department Waste Comparison"
            )

            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

            # Department efficiency metrics
            st.subheader("Departmental Efficiency Metrics")

            # Add per-employee metrics if data available
            if 'employee_count' in st.session_state:
                efficiency_df = dept_df.copy()
                efficiency_df["Waste per Employee"] = efficiency_df["Total Waste (kg)"] / st.session_state.employee_count
                st.dataframe(efficiency_df, height=200, use_container_width=True)
            else:
                st.info("Employee data not available. Add employee counts to see efficiency metrics.")

    # Show raw data option
    if st.checkbox("📋 Show Raw Data"):
        st.dataframe(
            historical_data[waste_type],
            height=300,
            use_container_width=True
        )

    # Future Improvements Section
    st.sidebar.markdown("""
    ---
    ### 🚀 Upcoming Features
    - Real-time data integration
    - Waste composition analysis
    - Predictive maintenance alerts
    - Custom report generation
    - Environmental impact metrics
    """)

    # Page routing
    if not st.session_state['authenticated']:
        # Show authentication page
        show_auth_page()
    else:
        # Get current page from session state or default to dashboard
        current_page = st.session_state.get('current_page', 'dashboard')

        