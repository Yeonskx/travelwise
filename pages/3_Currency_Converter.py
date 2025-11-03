import streamlit as st
from utils.currency_api import get_exchange_rate

# --- LOGIN PROTECTION ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Please log in or create an account to access this page.")
    st.stop()  # stops execution of the rest of the page

st.set_page_config(page_title="Currency Converter", page_icon="💱")
st.title("💱 Currency Converter")
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

# --- SIDEBAR LOGOUT ---
if st.session_state["logged_in"]:
    user = st.session_state["user"]
    st.sidebar.markdown(f"👋 **Welcome, {user['firstname']}!**")
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["user"] = {}
        st.rerun()