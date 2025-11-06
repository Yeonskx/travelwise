import streamlit as st
from utils.currency_api import get_exchange_rate

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

    
# --------------------------
# PAGE CONFIGURATION
# --------------------------
st.set_page_config(page_title="Currency Converter", layout="centered")

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
    st.warning("⚠️ Please log in or create an account to access this page.")
    st.stop()  # stops execution of the rest of the page

st.title("Currency Converter")
st.write("Convert one currency to another using live exchange rates.")

# --- Initialize session state for currencies if not exists ---
if "base_currency" not in st.session_state:
    st.session_state.base_currency = "USD"
if "target_currency" not in st.session_state:
    st.session_state.target_currency = "PHP"

# --- Common currencies for dropdowns ---
currencies = [
    "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "SGD", "PHP", "KRW", "INR"
]

# --- Currency selection with swap arrow ---
col1, col_arrow, col2 = st.columns([5, 1, 5])

with col1:
    base_currency = st.selectbox(
        "From Currency:", 
        currencies, 
        index=currencies.index(st.session_state.base_currency)
    )
    st.session_state.base_currency = base_currency

with col_arrow:
    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing to align with dropdowns
    if st.button("⇄", help="Swap currencies", use_container_width=True):
        # Swap the currencies
        temp = st.session_state.base_currency
        st.session_state.base_currency = st.session_state.target_currency
        st.session_state.target_currency = temp
        st.rerun()

with col2:
    target_currency = st.selectbox(
        "To Currency:", 
        currencies, 
        index=currencies.index(st.session_state.target_currency)
    )
    st.session_state.target_currency = target_currency

# --- Amount input ---
amount = st.number_input("Amount to Convert:", min_value=0.0, value=1.0, step=0.01)

# --- Convert button ---
if st.button("Convert", type="primary"):
    rate = get_exchange_rate(base_currency, target_currency)
    if rate:
        converted = amount * rate
        st.success(f"💰 {amount:.2f} {base_currency} = {converted:.2f} {target_currency}")
        st.caption(f"Exchange Rate: 1 {base_currency} = {rate:.4f} {target_currency}")
    else:
        st.error("⚠️ Could not fetch the exchange rate. Please check your internet connection or currency codes.")

with st.sidebar.expander("How Currency Converter Works", expanded=True):
    st.markdown("""
    The **Currency Converter** allows travelers to easily convert between popular
    global currencies using **live exchange rates**.

    **How to use it:**
    1. **Select Currencies:**  
       Choose your base and target currencies from the dropdown menus.  
       You can also click the **⇄** button to swap them instantly.

    2. **Enter an Amount:**  
       Type how much you want to convert whether it’s a few dollars or a full budget.

    3. **View Conversion Results:**  
       Click **Convert** to display the converted amount and current exchange rate.

    4. **Stay Updated:**  
       Rates are fetched live through the TravelWise **Currency API**, ensuring you
       always get the most recent conversion values.
    """)


# --- SIDEBAR LOGOUT ---
if st.session_state["logged_in"]:
    user = st.session_state["user"]
    st.sidebar.markdown(f"👋 **Welcome, {user['firstname']}!**")
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["user"] = {}
        st.rerun()