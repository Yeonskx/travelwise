import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="Travel Plan Dashboard", page_icon="🧳", layout="wide")

# --- LOGIN PROTECTION ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Please log in or create an account to access this page.")
    st.stop()

# --- CUSTOM CSS FOR DASHBOARD STYLING ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card-orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 1.5rem 0 1rem 0;
        padding-left: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- DASHBOARD HEADER ---
st.markdown('<p class="main-header">🧳 Travel Plan Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Plan your perfect trip with intelligent budget allocation and insights</p>', unsafe_allow_html=True)

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

# --- SIDEBAR: TRIP CONFIGURATION ---
with st.sidebar:
    st.markdown("Trip Configuration")
    
    st.session_state.destination_country = st.selectbox(
        "Destination", 
        ["Japan", "Korea", "Singapore", "Thailand", "USA", "France", "Italy", "Australia"],
        index=0
    )
    
    col_curr1, col_curr2 = st.columns(2)
    with col_curr1:
        st.session_state.home_currency = st.selectbox("Home", ["PHP", "USD", "EUR", "JPY", "KRW"])
    with col_curr2:
        st.session_state.destination_currency = st.selectbox("Dest", ["JPY", "KRW", "SGD", "THB", "USD", "EUR"])
    
    st.session_state.total_budget = st.number_input(
        "💵 Total Budget", 
        min_value=1000, 
        step=1000, 
        value=st.session_state.total_budget
    )
    
    st.session_state.duration_days = st.slider(
        "📅 Duration (Days)", 
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
        value=f"₱{total_budget:,.0f}",
        delta=None
    )

with metric_col2:
    st.metric(
        label="Trip Duration",
        value=f"{duration_days} days",
        delta=None
    )

with metric_col3:
    st.metric(
        label="Daily Allowance",
        value=f"₱{daily_allowance:,.0f}",
        delta=None
    )

with metric_col4:
    st.metric(
        label="Destination",
        value=st.session_state.destination_country,
        delta=None
    )

st.divider()

# --- MAIN DASHBOARD LAYOUT ---
left_col, right_col = st.columns([3, 2])

with left_col:
    # --- BUDGET ALLOCATION ---
    st.markdown('<p class="section-title">💰 Budget Allocation</p>', unsafe_allow_html=True)
    
    categories = [
        ("Accommodation", "accommodation"),
        ("Food & Dining", "food"),
        ("Transportation", "transport"),
        ("Shopping", "shopping"),
        ("Miscellaneous", "misc")
    ]
    
    allocations = {}
    
    col_input1, col_input2 = st.columns(2)
    for i, (label, key) in enumerate(categories):
        with (col_input1 if i % 2 == 0 else col_input2):
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
    budget_col1, budget_col2 = st.columns(2)
    with budget_col1:
        st.metric("Total Allocated", f"₱{total_allocated:,.0f}")
    with budget_col2:
        if remaining_budget < 0:
            st.metric("Over Budget", f"₱{abs(remaining_budget):,.0f}", delta=f"-₱{abs(remaining_budget):,.0f}", delta_color="inverse")
        else:
            st.metric("Remaining", f"₱{remaining_budget:,.0f}", delta=f"₱{remaining_budget:,.0f}")
    
    st.divider()
    
    # --- PIE CHART ---
    st.markdown('<p class="section-title">Spending Distribution</p>', unsafe_allow_html=True)
    
    alloc_df = pd.DataFrame(list(allocations.items()), columns=["Category", "Amount"])
    alloc_df = alloc_df[alloc_df["Amount"] > 0]  # Only show allocated categories
    
    if not alloc_df.empty:
        fig_pie = px.pie(
            alloc_df,
            values="Amount",
            names="Category",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("👆 Allocate your budget above to see the distribution chart")

with right_col:
    # --- ALLOCATION TABLE ---
    st.markdown('<p class="section-title">Allocation Breakdown</p>', unsafe_allow_html=True)
    
    if not alloc_df.empty:
        alloc_df["Percentage"] = round((alloc_df["Amount"] / total_budget) * 100, 1)
        alloc_df["Amount"] = alloc_df["Amount"].apply(lambda x: f"₱{x:,.0f}")
        alloc_df["Percentage"] = alloc_df["Percentage"].apply(lambda x: f"{x}%")
        
        st.dataframe(
            alloc_df,
            hide_index=True,
            use_container_width=True,
            height=250
        )
    else:
        st.info("No allocations yet")
    
    st.divider()
    
    # --- DAILY VS REMAINING ---
    st.markdown('<p class="section-title">Daily Budget Analysis</p>', unsafe_allow_html=True)
    
    chart_df = pd.DataFrame({
        "Category": ["Daily Allowance", "Remaining Budget"],
        "Amount": [daily_allowance, max(remaining_budget, 0)]
    })
    
    fig_bar = go.Figure(data=[
        go.Bar(
            x=chart_df["Category"],
            y=chart_df["Amount"],
            text=chart_df["Amount"].apply(lambda x: f"₱{x:,.0f}"),
            textposition='outside',
            marker=dict(
                color=['#667eea', '#38ef7d'],
                line=dict(color='rgba(0,0,0,0.2)', width=2)
            )
        )
    ])
    
    fig_bar.update_layout(
        height=300,
        margin=dict(t=20, b=20, l=20, r=20),
        yaxis_title="Amount (₱)",
        showlegend=False
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Budget tip
    if daily_allowance < 2000:
        st.warning("💡 **Tip:** Your daily allowance is quite low — consider increasing your budget!")
    else:
        st.success("✅ Your daily allowance looks great for a comfortable trip!")

st.divider()

# --- CURRENCY TREND SECTION ---
st.markdown('<p class="section-title">📈 Exchange Rate Trend (7-Day Simulation)</p>', unsafe_allow_html=True)

col_trend1, col_trend2 = st.columns([3, 1])

with col_trend1:
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
        line=dict(color='#00CC96', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(0, 204, 150, 0.1)'
    ))
    
    fig_line.update_layout(
        height=300,
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis_title="Date",
        yaxis_title=f"Rate ({st.session_state.home_currency} → {st.session_state.destination_currency})",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_line, use_container_width=True)

with col_trend2:
    st.markdown("### 📊 Stats")
    st.metric("Current Rate", "₱0.40")
    st.metric("7-Day High", "₱0.42", delta="+0.02")
    st.metric("7-Day Low", "₱0.39", delta="-0.01")
    st.caption("💡 Simulated data for demonstration")

st.divider()

# --- TRAVEL SUMMARY CARD ---
st.markdown('<p class="section-title">📋 Travel Plan Summary</p>', unsafe_allow_html=True)

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:
    st.markdown(f"""
    **Destination**  
    {st.session_state.destination_country} ({st.session_state.destination_currency})
    
    **Home Currency**  
    {st.session_state.home_currency}
    """)

with summary_col2:
    st.markdown(f"""
    **Total Budget**  
    ₱{total_budget:,.0f}
    
    **Duration**  
    {duration_days} days
    """)

with summary_col3:
    st.markdown(f"""
    **Daily Allowance**  
    ₱{daily_allowance:,.0f}
    
    **✅ Status**  
    {'Budget OK' if remaining_budget >= 0 else 'Over Budget'}
    """)

st.success("✨ Your travel plan is ready! Use this dashboard to track and optimize your trip budget.")