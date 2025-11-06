import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Hide pages function
def hide_pages_when_not_logged_in():
    is_logged_in = st.session_state.get('logged_in', False)
    
    if not is_logged_in:
        hide_pages_css = """
        <style>
            [data-testid="stSidebarNav"] li:nth-child(3),
            [data-testid="stSidebarNav"] li:nth-child(4),
            [data-testid="stSidebarNav"] li:nth-child(5),
            [data-testid="stSidebarNav"] li:nth-child(6),
            [data-testid="stSidebarNav"] li:nth-child(7) {
                display: none;
            }
        </style>
        """
        st.markdown(hide_pages_css, unsafe_allow_html=True)

hide_pages_when_not_logged_in()


# --- LOGIN PROTECTION ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in or create an account to access this page.")
    st.stop()

# --- CUSTOM CSS FOR DASHBOARD STYLING ---
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.3rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #334155;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }
    .stMetric {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# --- DASHBOARD HEADER ---
st.markdown('<p class="main-header">Travel Plan Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Plan and track your trip budget efficiently</p>', unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE FOR INPUTS ---
if "home_currency" not in st.session_state:
    st.session_state.home_currency = "PHP"
if "destination_country" not in st.session_state:
    st.session_state.destination_country = "Japan"
if "destination_currency" not in st.session_state:
    st.session_state.destination_currency = "JPY"
if "total_budget" not in st.session_state:
    st.session_state.total_budget = 30000
if "duration_days" not in st.session_state:
    st.session_state.duration_days = 7

# --- DESTINATION TO CURRENCY MAPPING ---
destination_currency_map = {
    "Japan": "JPY",
    "Korea": "KRW",
    "Singapore": "SGD",
    "Thailand": "THB",
    "USA": "USD",
    "France": "EUR",
    "Italy": "EUR",
    "Australia": "AUD"
}

# --- SIDEBAR: TRIP CONFIGURATION ---
with st.sidebar:
    st.subheader("Trip Configuration")
    
    st.session_state.destination_country = st.selectbox(
        "Destination", 
        ["Japan", "Korea", "Singapore", "Thailand", "USA", "France", "Italy", "Australia"],
        index=0
    )

    # Automatically set the destination currency based on selected destination
    auto_currency = destination_currency_map.get(st.session_state.destination_country, "USD")
    st.session_state.destination_currency = auto_currency
    
    col_curr1, col_curr2 = st.columns(2)
    with col_curr1:
        st.session_state.home_currency = st.selectbox("Home Currency", ["PHP", "USD", "EUR", "JPY", "KRW"])
    with col_curr2:
        st.text_input("Destination Currency", st.session_state.destination_currency, disabled=True)

    st.session_state.total_budget = st.number_input(
        "Total Budget", 
        min_value=1000, 
        step=1000, 
        value=st.session_state.total_budget
    )
    
    st.session_state.duration_days = st.slider(
        "Duration (Days)", 
        1, 30, 
        st.session_state.duration_days
    )
    
    st.divider()
    
    # Logout
    user = st.session_state["user"]
    st.markdown(f"👋 **Welcome, {user['firstname']}!**")
    if st.button("Logout", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["user"] = {}
        st.rerun()

# --- KEY METRICS ROW ---
total_budget = st.session_state.total_budget
duration_days = st.session_state.duration_days
daily_allowance = total_budget / duration_days

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.metric(
        label="Total Budget",
        value=f"₱{total_budget:,.0f}"
    )

with metric_col2:
    st.metric(
        label="Trip Duration",
        value=f"{duration_days} days"
    )

with metric_col3:
    st.metric(
        label="Daily Allowance",
        value=f"₱{daily_allowance:,.0f}"
    )

with metric_col4:
    st.metric(
        label="Destination",
        value=st.session_state.destination_country
    )

# --- BUDGET ALLOCATION ---
st.markdown('<p class="section-title">Budget Allocation</p>', unsafe_allow_html=True)

categories = [
    ("Accommodation", "accommodation"),
    ("Food & Dining", "food"),
    ("Transportation", "transport"),
    ("Shopping", "shopping"),
    ("Miscellaneous", "misc")
]

allocations = {}

col_input1, col_input2, col_input3 = st.columns(3)
for i, (label, key) in enumerate(categories):
    col_idx = i % 3
    with (col_input1 if col_idx == 0 else col_input2 if col_idx == 1 else col_input3):
        allocations[label] = st.number_input(
            label,
            min_value=0,
            step=500,
            value=0,
            key=key
        )

# Calculate totals
total_allocated = sum(allocations.values())
remaining_budget = total_budget - total_allocated

# Budget status
st.markdown("### Budget Status")
budget_col1, budget_col2, budget_col3 = st.columns(3)
with budget_col1:
    st.metric("Total Allocated", f"₱{total_allocated:,.0f}")
with budget_col2:
    if remaining_budget < 0:
        st.metric("Over Budget", f"₱{abs(remaining_budget):,.0f}", delta=f"-₱{abs(remaining_budget):,.0f}", delta_color="inverse")
    else:
        st.metric("Remaining", f"₱{remaining_budget:,.0f}", delta=f"₱{remaining_budget:,.0f}")
with budget_col3:
    allocation_pct = (total_allocated / total_budget * 100) if total_budget > 0 else 0
    st.metric("Allocated", f"{allocation_pct:.1f}%")

# --- VISUALIZATION SECTION ---
st.markdown('<p class="section-title">Budget Overview</p>', unsafe_allow_html=True)

viz_col1, viz_col2 = st.columns(2)

with viz_col1:
    st.markdown("#### Spending Distribution")
    
    alloc_df = pd.DataFrame(list(allocations.items()), columns=["Category", "Amount"])
    alloc_df = alloc_df[alloc_df["Amount"] > 0]
    
    if not alloc_df.empty:
        fig_pie = px.pie(
            alloc_df,
            values="Amount",
            names="Category",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            showlegend=False,
            height=350,
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Allocate your budget to see the distribution chart")

with viz_col2:
    st.markdown("#### Allocation Breakdown")
    
    if not alloc_df.empty:
        alloc_df["Percentage"] = round((alloc_df["Amount"] / total_budget) * 100, 1)
        alloc_df["Daily"] = round(alloc_df["Amount"] / duration_days, 0)
        alloc_df["Amount"] = alloc_df["Amount"].apply(lambda x: f"₱{x:,.0f}")
        alloc_df["Daily"] = alloc_df["Daily"].apply(lambda x: f"₱{x:,.0f}")
        alloc_df["Percentage"] = alloc_df["Percentage"].apply(lambda x: f"{x}%")
        
        st.dataframe(
            alloc_df,
            hide_index=True,
            use_container_width=True,
            height=280
        )
    else:
        st.info("No allocations yet")

# --- EXCHANGE RATE TREND ---
st.markdown('<p class="section-title">Exchange Rate Trend</p>', unsafe_allow_html=True)

trend_col1, trend_col2 = st.columns([3, 1])

with trend_col1:
    # Simulate 7-day trend
    days = pd.date_range(date.today() - timedelta(days=6), date.today())
    simulated_rates = [0.39, 0.40, 0.41, 0.42, 0.405, 0.395, 0.40]
    
    trend_df = pd.DataFrame({
        "Date": days,
        "Rate": simulated_rates
    })
    
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=trend_df["Date"],
        y=trend_df["Rate"],
        mode='lines+markers',
        name='Exchange Rate',
        line=dict(color='#3b82f6', width=2),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)'
    ))
    
    fig_line.update_layout(
        height=250,
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis_title="Date",
        yaxis_title=f"Rate ({st.session_state.home_currency} to {st.session_state.destination_currency})",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_line, use_container_width=True)

with trend_col2:
    st.markdown("#### Statistics")
    st.metric("Current Rate", "₱0.40")
    st.metric("7-Day High", "₱0.42", delta="+0.02")
    st.metric("7-Day Low", "₱0.39", delta="-0.01")
    st.caption("Simulated data for demonstration")

# --- INSIGHTS ---
st.markdown('<p class="section-title">Budget Insights</p>', unsafe_allow_html=True)

insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    if daily_allowance < 2000:
        st.warning("Your daily allowance is below ₱2,000. Consider increasing your budget for a more comfortable trip.")
    elif daily_allowance > 5000:
        st.success("Your daily allowance is generous and should provide a comfortable travel experience.")
    else:
        st.info("Your daily allowance is adequate for a standard travel experience.")

with insight_col2:
    if remaining_budget < 0:
        st.error(f"You are over budget by ₱{abs(remaining_budget):,.0f}. Consider adjusting your allocations.")
    elif remaining_budget > total_budget * 0.2:
        st.info(f"You have ₱{remaining_budget:,.0f} unallocated. Consider planning for additional activities.")
    else:
        st.success("Your budget allocation looks well balanced.")

with st.sidebar.expander("About the Travel Plan Dashboard", expanded=True):
    st.markdown("""
    The **Travel Plan Dashboard** helps you plan and track your overall travel budget.

    **Quick Guide:**
    - **Set Trip Details:** Choose your destination, duration, and total budget.
    - **Allocate Funds:** Distribute your budget across categories like Food, Transport, and Shopping.
    - **View Analytics:** Track totals, remaining funds, and category breakdowns through charts.
    - **Check Exchange Trends:** Monitor simulated exchange rate movements for better cost planning.
    """)
