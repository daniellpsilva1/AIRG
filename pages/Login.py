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
import os
import uuid

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
                # Store the session in Streamlit's session state
                st.session_state['user'] = session['user']
                # Redirect to the main page
                st.experimental_set_query_params()
                st.experimental_rerun()
            else:
                st.error("Failed to exchange code for session.")
        else:
            st.warning("No OAuth callback parameters found.")
    except Exception as e:
        st.error(f"An error occurred during OAuth callback: {str(e)}")
    
    return None

def get_image(image_path, default_image_path):
    if os.path.exists(image_path):
        return image_path
    elif os.path.exists(default_image_path):
        return default_image_path
    else:
        return None

def main():
    # Configure Supabase authentication
    logo_path = "public/streamlit-logo.svg"
    default_logo_path = "path/to/default/logo.svg"  # Replace with an actual path
    
    logo = get_image(logo_path, default_logo_path)

    left_co, cent_co, last_co = st.columns(3)

    with cent_co:
        if logo:
            st.image(logo)
        else:
            st.write("Logo image not found")

    # Check if we're handling an OAuth callback
    if 'code' in st.experimental_get_query_params():
        handle_oauth_callback()
    elif 'user' in st.session_state:
        # User is already authenticated
        handle_authenticated_session(st.session_state['user'])
    else:
        try:
            # Generate a unique state for this login attempt
            state = str(uuid.uuid4())
            st.session_state['oauth_state'] = state

            session = login_form(
                url=SUPABASE_URL,
                apiKey=SUPABASE_KEY,
                providers=["github", "google"],
                options={
                    "redirectTo": st.experimental_get_query_params().get('redirect', [''])[0],
                    "queryParams": {"state": state}
                }
            )
            
            if session:
                handle_authenticated_session(session)
            else:
                unauthenticated_menu()
        except FileNotFoundError as e:
            st.error(f"Error loading authentication form: {str(e)}")
            st.info("Please check if all required files are present in the streamlit_supabase_auth package.")

if __name__ == "__main__":
    main()


