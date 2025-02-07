# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os
from datetime import datetime
from dotenv import load_dotenv
from dropbox_client import DropboxClientManager

# Load environment variables
load_dotenv()

# Initialize the Dropbox client manager
@st.cache_resource
def get_dropbox_manager():
    """Create or get cached DropboxClientManager"""
    try:
        return DropboxClientManager()
    except ValueError as e:
        st.error(f"Configuration Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error initializing Dropbox client: {str(e)}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data(dropbox_path):
    """Load data from Dropbox with caching"""
    try:
        manager = get_dropbox_manager()
        if manager is None:
            return None
            
        content = manager.get_file(dropbox_path)
        if content is None:
            return None
            
        # Read CSV from bytes content
        df = pd.read_csv(io.BytesIO(content))
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Set up the Streamlit page
st.set_page_config(page_title="Sample Analysis Dashboard", layout="wide")

# Debug information (will be hidden in production)
if st.secrets.get("show_debug", False):
    st.write("Debug Information:")
    st.write(f"APP_KEY exists: {bool(os.getenv('DROPBOX_APP_KEY'))}")
    st.write(f"APP_SECRET exists: {bool(os.getenv('DROPBOX_APP_SECRET'))}")
    st.write(f"REFRESH_TOKEN exists: {bool(os.getenv('DROPBOX_REFRESH_TOKEN'))}")

# Your Dropbox file path
DROPBOX_PATH = '/streamlit_test/data/samples_data.csv'  # Update this to your file path

# Load data
df = load_data(DROPBOX_PATH)

if df is not None:
    # Rest of your dashboard code...
    [Previous dashboard code remains the same]
else:
    st.error("""
    Unable to load data from Dropbox. Please check:
    1. Your Dropbox credentials are correctly set in the environment variables
    2. The file path is correct
    3. Your refresh token has the correct permissions
    """)
    
    # Show the file path for verification
    st.info(f"Attempting to access file at: {DROPBOX_PATH}")