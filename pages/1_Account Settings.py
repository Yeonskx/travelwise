import streamlit as st
from utils.auth import init_db, add_user, verify_user, email_exists
import pandas as pd
import sqlite3
import time

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


# --- Initialize database ---
init_db()

# --- Basic CSS ---
st.markdown("""
<style>
    .main { max-width: 700px; margin: 0 auto; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: center;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        padding: 0.5rem;
        font-weight: 500;
    }
    h1 { text-align: center; font-weight: 600; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- Session Defaults ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = {}

# --- Header ---
st.title("✈️ TravelWise")

# --- Tabs for Login / Signup ---
tab1, tab2 = st.tabs(["Login", "Sign Up"])

# ==================== LOGIN ====================
with tab1:
    st.subheader("Welcome back")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_btn"):
        if not email or not password:
            st.warning("Please fill in all fields")
        else:
            user = verify_user(email, password)
            if user:
                st.session_state["logged_in"] = True
                st.session_state["user"] = {
                    "email": user[0],
                    "firstname": user[2],
                    "lastname": user[3],
                    "country": user[4],
                    "role": user[5]
                }
                if user[5] == "admin":
                    st.success(f"Welcome, Admin {user[2]} 👑")
                else:
                    st.success(f"Welcome, {user[2]}!")
                    time.sleep(1)
            else:
                st.error("Invalid credentials")

# ==================== SIGN UP ====================
with tab2:
    st.subheader("Create account")

    # --- Responsive form layout ---
    st.markdown("""
    <style>
        @media (max-width: 768px) {
            /* Stack the Streamlit columns vertically */
            div[data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                display: block;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    # Two columns for desktop, stacked automatically on mobile
    col1, col2 = st.columns(2)

    with col1:
        firstname = st.text_input("First Name")
        lastname = st.text_input("Last Name")
        country = st.text_input("Country")

    with col2:
        email_signup = st.text_input("Email", key="signup_email")
        password_signup = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up", key="signup_btn"):
        if not all([firstname, lastname, email_signup, country, password_signup, confirm_password]):
            st.warning("Please fill in all fields")
        elif password_signup != confirm_password:
            st.error("Passwords don't match")
        elif email_exists(email_signup):
            st.error("Email already registered")
        else:
            add_user(email_signup, password_signup, firstname, lastname, country)
            st.success("Account created! You can now log in.")


# ==================== INLINE ADMIN DASHBOARD ====================
if st.session_state["logged_in"] and st.session_state["user"]["role"] == "admin":
    st.markdown("---")
    st.subheader("🛠️ Admin Dashboard")

    def get_all_users():
        conn = sqlite3.connect("database/users.db")
        df = pd.read_sql_query("SELECT firstname, lastname, email, country, role FROM users", conn)
        conn.close()
        return df

    def delete_user(email):
        conn = sqlite3.connect("database/users.db")
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()
        conn.close()

    users_df = get_all_users()
    search = st.text_input("🔍 Search by name, email, or country")

    if search:
        mask = users_df.apply(lambda row: search.lower() in row.astype(str).str.lower().to_list(), axis=1)
        filtered_df = users_df[mask]
    else:
        filtered_df = users_df

    st.dataframe(filtered_df, use_container_width=True)

    st.markdown("### 🗑️ Delete a User")
    col1, col2 = st.columns([3, 1])
    with col1:
        email_to_delete = st.text_input("Enter user email to delete")
    with col2:
        if st.button("Delete User"):
            if not email_to_delete:
                st.warning("Please enter an email.")
            elif email_to_delete == "admin@travelwise.com":
                st.error("Cannot delete the main admin account.")
            else:
                delete_user(email_to_delete)
                st.success(f"✅ User '{email_to_delete}' has been deleted.")
                st.rerun()


with st.sidebar.expander("About TravelWise", expanded=True):
    st.write(
        "TravelWise is an AI-powered travel planner that helps users design smarter itineraries, "
        "manage budgets, and explore destinations effortlessly. Its mission is to make travel "
        "planning simple, personalized, and stress-free."
    )

# --- SIDEBAR LOGOUT ---
if st.session_state["logged_in"]:
    user = st.session_state["user"]
    st.sidebar.markdown(f"👋 **Welcome, {user['firstname']}!**")
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["user"] = {}
        st.rerun()
