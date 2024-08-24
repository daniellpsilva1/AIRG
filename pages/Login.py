import streamlit as st
from pages.menu import menu, menu_with_redirect, unauthenticated_menu
from streamlit_supabase_auth import login_form, logout_button
from supabase import create_client, Client
import streamlit_shadcn_ui as ui
import shutil
import logging
from bs4 import BeautifulSoup
import pathlib
from urllib.parse import parse_qs, urlparse

st.set_option("client.showSidebarNavigation", False)
st.set_page_config(
    page_title="Streamlit SaaS Starter",
    page_icon="🌍",
    layout="centered"
)

# Initialization with Supabase credentials
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Streamlit SaaS Starter Login Page")

def handle_authenticated_session(session):
    menu()
    # Store user session in Streamlit session state
    st.session_state['user'] = session['user']

    # Perform checks of user session here. 
    st.session_state.role = "user"

    # Update query param to reset url fragments
    st.query_params.login = ["success"]

    with st.sidebar:
        st.markdown(f"**Logged in as: *{session['user']['email']}***")
        if logout_button(url=SUPABASE_URL, apiKey=SUPABASE_KEY):
            print("Logging out.")

def handle_oauth_callback():
    try:
        # Get the full URL of the current page
        url = st.experimental_get_query_params()
        
        # Check if we have a code and state in the URL
        if 'code' in url and 'state' in url:
            code = url['code'][0]
            state = url['state'][0]
            
            # Exchange the code for a session
            session = supabase.auth.exchange_code_for_session(code)
            
            if session:
                st.success("Successfully logged in!")
                return session
            else:
                st.error("Failed to exchange code for session.")
        else:
            st.warning("No OAuth callback parameters found.")
    except Exception as e:
        st.error(f"An error occurred during OAuth callback: {str(e)}")
    
    return None

def main():
    # Configure Supabase authentication
    logo = "public/streamlit-logo.svg"

    left_co, cent_co, last_co = st.columns(3)

    with cent_co:
        st.image(logo)

    # Check if we're handling an OAuth callback
    callback_session = handle_oauth_callback()
    if callback_session:
        handle_authenticated_session(callback_session)
    else:
        session = login_form(
            url=SUPABASE_URL,
            apiKey=SUPABASE_KEY,
            providers=["github", "google"]
        )
        
        if session:
            handle_authenticated_session(session)
        else:
            unauthenticated_menu()

if __name__ == "__main__":
    main()


