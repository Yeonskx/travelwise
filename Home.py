import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(page_title="TravelWise", page_icon="🌍", layout="wide")

# --- SESSION DEFAULTS ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = {}

# --- CUSTOM STYLES ---
st.markdown("""
<style>
    .main {padding: 2rem 3rem;}
    h1 {font-size: 2.2rem; font-weight: 600; margin-bottom: 0.5rem;}
    p.desc {color: #555; font-size: 1rem; margin-bottom: 2rem;}
    .center {text-align: center; margin-top: 6rem;}
    .stButton>button {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR HEADER ---
st.sidebar.header("🌍 TravelWise")
if st.session_state["logged_in"]:
    user = st.session_state["user"]
    st.sidebar.markdown(f"👋 **{user['firstname']} {user['lastname']}**")
    st.sidebar.divider()
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["user"] = {}
        st.rerun()
else:
    st.sidebar.info("🔑 Please log in to access all features.")

# --- MAIN CONTENT ---
if st.session_state["logged_in"]:
    user = st.session_state["user"]
    st.title("Welcome to TravelWise 🌍")
    st.markdown(
        f"**Hello, {user['firstname']}!** Start exploring personalized travel tools, budget planners, and insights designed just for you."
    )
    st.write("Use the sidebar to navigate through TravelWise features.")
else:
    st.markdown(
        """
        <div class='center'>
            <h1>Welcome to 🌍 TravelWise</h1>
            <p class='desc'>
                Your smart travel companion — plan budgets, track conversions, and get AI-powered trip recommendations.
            </p>
            <p>Login or create an account to start your journey.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
