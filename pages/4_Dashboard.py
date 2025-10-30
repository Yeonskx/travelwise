import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="Travel Plan Creator", page_icon="🧳", layout="centered")

# --- LOGIN PROTECTION ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Please log in or create an account to access this page.")
    st.stop()

# --- PAGE HEADER ---
st.title("🧳 Create Your Travel Plan")
st.markdown("Plan your next trip by entering your destination, budget, and stay details below. 🌍")

st.divider()

# --- TRIP DETAILS INPUT ---
st.subheader("🌐 Trip Details")

col1, col2 = st.columns(2)
with col1:
    home_currency = st.selectbox("Home Currency", ["PHP", "USD", "EUR", "JPY", "KRW"])
    total_budget = st.number_input("Total Travel Budget", min_value=1000, step=500, value=30000)
with col2:
    destination_country = st.selectbox("Destination Country", ["Japan", "Korea", "Singapore", "Thailand", "USA", "France"])
    destination_currency = st.selectbox("Destination Currency", ["JPY", "KRW", "SGD", "THB", "USD", "EUR"])
    duration_days = st.slider("Duration of Stay (Days)", 1, 30, 7)

st.divider()

# --- BUDGET ALLOCATION ---
st.subheader("💰 Budget Allocation")
st.markdown("Allocate your total budget across different spending categories:")

categories = [
    "Accommodation / Hotels",
    "Food & Dining",
    "Transportation / Fare",
    "Shopping",
    "Miscellaneous"
]

allocations = {}
colA, colB = st.columns(2)
for i, category in enumerate(categories):
    with (colA if i % 2 == 0 else colB):
        allocations[category] = st.number_input(
            f"{category} (₱)", min_value=0, step=500, value=0
        )

# --- CALCULATE TOTALS ---
total_allocated = sum(allocations.values())
remaining_budget = total_budget - total_allocated

st.markdown("---")
st.write("### 🧾 Allocation Summary")

# --- ALLOCATION DATAFRAME ---
alloc_df = pd.DataFrame(list(allocations.items()), columns=["Category", "Amount (PHP)"])
alloc_df["Percentage"] = round((alloc_df["Amount (PHP)"] / total_budget) * 100, 1)

col1, col2 = st.columns([2, 1])
with col1:
    fig = px.pie(
        alloc_df,
        values="Amount (PHP)",
        names="Category",
        title="Budget Allocation per Category",
        color_discrete_sequence=px.colors.qualitative.Vivid,
        hole=0.35,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.dataframe(alloc_df, hide_index=True, use_container_width=True)

st.metric("Total Allocated", f"₱{total_allocated:,.0f}")
if remaining_budget < 0:
    st.warning(f"⚠️ You’ve exceeded your budget by ₱{abs(remaining_budget):,.0f}")
else:
    st.info(f"💡 Remaining Unallocated Budget: ₱{remaining_budget:,.0f}")

st.divider()

# --- DAILY ALLOWANCE ---
st.subheader("📊 Daily Allowance vs Remaining Funds")
daily_allowance = total_budget / duration_days
st.metric("Daily Allowance", f"₱{daily_allowance:,.2f}")

chart_df = pd.DataFrame({
    "Category": ["Daily Allowance", "Remaining Funds"],
    "Amount (PHP)": [daily_allowance, remaining_budget]
})

fig_bar = px.bar(
    chart_df,
    x="Category",
    y="Amount (PHP)",
    color="Category",
    text_auto=True,
    title="Comparison of Daily Allowance and Remaining Funds",
    color_discrete_sequence=["#636EFA", "#EF553B"]
)
st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

if daily_allowance < 2000:
    st.warning("💡 Tip: Your daily allowance is quite low — consider increasing your budget or reducing your duration.")
else:
    st.success("✅ Your daily allowance looks good for a balanced trip!")

st.divider()

# --- LINE CHART: SIMULATED CURRENCY TREND ---
st.subheader("📈 Simulated Currency Trend (Example)")

# Simulate 7-day trend around a random baseline value
days = pd.date_range(date.today() - timedelta(days=6), date.today())
simulated_rates = [0.39, 0.40, 0.41, 0.42, 0.405, 0.395, 0.40]

trend_df = pd.DataFrame({
    "Date": days,
    "Rate (₱ to Foreign)": simulated_rates
})

fig_line = px.line(
    trend_df,
    x="Date",
    y="Rate (₱ to Foreign)",
    title=f"Simulated Exchange Rate Trend ({home_currency} → {destination_currency})",
    markers=True,
    line_shape="spline",
    color_discrete_sequence=["#00CC96"]
)
st.plotly_chart(fig_line, use_container_width=True)

st.caption("Simulated data only for visualization — not live exchange rates.")
st.divider()

# --- PLAN SUMMARY ---
st.subheader("📋 Travel Plan Summary")

st.write(f"**Destination:** {destination_country} ({destination_currency})")
st.write(f"**Home Currency:** {home_currency}")
st.write(f"**Total Budget:** ₱{total_budget:,.0f}")
st.write(f"**Duration:** {duration_days} days")

st.info("✅ Your travel plan is ready! You can now use this data for Statistics, Visualizations, or AI Recommendations.")

st.divider()

# --- SIDEBAR LOGOUT ---
user = st.session_state["user"]
st.sidebar.markdown(f"👋 **Welcome, {user['firstname']}!**")
if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.session_state["user"] = {}
    st.experimental_rerun()
