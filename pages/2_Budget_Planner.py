import streamlit as st
import pandas as pd
from datetime import date

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
    st.stop()  # stops execution of the rest of the page

# --------------------------
# PAGE CONFIGURATION
# --------------------------
st.set_page_config(page_title="Budget Planner", layout="centered")

st.title("Budgeting Tool")
st.markdown(
    "<p style='text-align:center;'>Track your daily travel expenses, set spending limits, and keep your budget on track.</p>",
    unsafe_allow_html=True
)

# --------------------------
# SESSION STATE SETUP
# --------------------------
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Amount"])

# --------------------------
# INPUT FORM
# --------------------------
st.markdown("### Add Expense")

with st.form("expense_form", clear_on_submit=True):
    expense_date = st.date_input("Select Date", value=date.today())
    category = st.selectbox(
        "Budget Category",
        ["Flights", "Accommodation", "Food", "Transportation", "Entertainment", "Shopping", "Miscellaneous"]
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        amount = st.number_input(
            "Amount Spent (₱)",
            min_value=0,
            step=100,   # Step by ₱100
            format="%d"
        )

    submitted = st.form_submit_button("➕ Add Expense")

    if submitted:
        if amount > 0:
            new_data = pd.DataFrame({
                "Date": [expense_date],
                "Category": [category],
                "Amount": [amount]
            })
            st.session_state.expenses = pd.concat([st.session_state.expenses, new_data], ignore_index=True)
            st.success(f"Added ₱{amount:,.2f} to {category} for {expense_date}.")
        else:
            st.warning("Please enter a valid amount.")

# --------------------------
# SPENDING LIMIT SECTION
# --------------------------
st.markdown("### Set Spending Limit")
limit = st.number_input(
    "Enter your total budget limit (₱)",
    min_value=0,
    step=100,
    format="%d"
)

# --------------------------
# SUMMARY AND TABLE
# --------------------------
if not st.session_state.expenses.empty:
    st.markdown("### Budget Summary")

    total_spent = st.session_state.expenses["Amount"].sum()
    remaining = limit - total_spent if limit > 0 else None

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Spent", f"₱{total_spent:,.2f}")
    with col2:
        if limit > 0:
            st.metric("Remaining Budget", f"₱{remaining:,.2f}")
        else:
            st.info("Set a spending limit to see your remaining budget.")

    # Expense breakdown table with date tracking
    st.markdown("### Expense Details")
    st.dataframe(
        st.session_state.expenses.style.format({
            "Amount": "₱{:.2f}",
            "Date": lambda d: d.strftime("%Y-%m-%d")
        }),
        use_container_width=True
    )

# --------------------------
# CLEAR DATA OPTION
# --------------------------
if st.button("🗑️ Clear All Data"):
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Amount"])
    st.rerun()
else:
    st.info("Add some expenses to start tracking your budget.")

with st.sidebar.expander("How Budget Planner Works", expanded=True):
    st.markdown("""
    The **Budget Planner** helps you keep track of your travel expenses while staying
    within your planned budget.

    **Here's how to use it:**
    1. **Add Expenses:**  
       Record your daily travel spending by selecting a date, category, and amount.  
       Categories include Flights, Food, Transportation, Accommodation, and more.

    2. **Set a Spending Limit:**  
       Enter your total trip budget to monitor your remaining balance as you log expenses.

    3. **Track Your Summary:**  
       Instantly view your **Total Spent** and **Remaining Budget** through dynamic metrics.

    4. **View Expense Details:**  
       A detailed table lists all your recorded expenses with date and category breakdowns.

    5. **Clear or Restart:**  
       You can reset your budget and expenses anytime using the **🗑️ Clear All Data** button.
    """)


# --- SIDEBAR LOGOUT ---
if st.session_state["logged_in"]:
    user = st.session_state["user"]
    st.sidebar.markdown(f"👋 **Welcome, {user['firstname']}!**")
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["user"] = {}
        st.rerun()
